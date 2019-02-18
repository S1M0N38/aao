import datetime

from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from aao.spiders.spider import Spider
from aao.spiders import sports


class SpiderBwin(Spider):
    bookmaker = 'bwin'
    base_url = 'https://sports.bwin.com/en/sports#'

    def __init__(self, *args, **kwargs):
        kwargs = self._load_env_config(kwargs)
        super().__init__(*args, **kwargs)
        self._soccer = Soccer(self)

    @property
    def soccer(self):
        return self._soccer


class Soccer(sports.Soccer):

    def __init__(self, spider):
        super().__init__(spider)

    def _request_page(self, page=0, events_only=False):
        self.log.debug(
            f'requesting page {page + 1} {self.country} - {self.league} …')
        url = self.base_url
        if not events_only:
            url = (f'{self.base_url}categoryIds=25,359,31,190,261&')
        url += f'leagueIds={self._league}&page={page}&sportId=4'
        self.browser.get(url)
        locator = (By.XPATH, '//div[@id="markets-container"]//td')
        try:
            self.wait.until(EC.visibility_of_all_elements_located(locator))
        except TimeoutException:
            msg = f'No data found for {self.country} - {self.league}.'
            self.log.error(msg)
            raise KeyError(f'{msg} This competition does not have odds')

    def _page_number(self):
        try:
            class_name = 'markets-pager__pages-count'
            page = self.browser.find_element_by_class_name(class_name)
            page_number = int(page.text.split(' ')[-2])
        except NoSuchElementException:
            page_number = 0
        return page_number

    def _get_rows(self, events_only=False):
        page_number = 1
        full_time_result, under_over, draw_no_bet = [], [], []
        both_teams_to_score, double_chance = [], []
        rows_dict = {'full_time_result': [], 'under_over': [],
                     'draw_no_bet': [], 'both_teams_to_score': [],
                     'double_chance': []}
        if not events_only:
            page_number = self.soccer._page_number()
        for page in range(page_number):
            self._request_page(page=page, events_only=events_only)
            xpath = ('//h2[@class="marketboard-event-group__header '
                     'marketboard-event-group__header--level-2"]/..')
            groups = self.browser.find_elements_by_xpath(xpath)
            for group in groups:
                market = group.find_element_by_tag_name('h2').text
                class_name = 'marketboard-event-group__item--sub-group'
                days = group.find_elements_by_class_name(class_name)
                for day in days:
                    date = day.find_element_by_tag_name('h2').text
                    values = day.find_elements_by_class_name(
                        'marketboard-event-group__item--event')
                    for value in values:
                        data = [date] + value.text.split('\n')
                        if market == 'Result (3Way)':
                            if data not in full_time_result:
                                full_time_result.append(data)
                        elif market == 'Number of goals?':
                            under_over = self._save_in_market(under_over, data)
                        elif market == '2Way - Who will win?':
                            draw_no_bet = self._save_in_market(
                                draw_no_bet, data)
                        elif market == 'Which team will score goals?':
                            rows_dict['both_teams_to_score'].append(data)
                            both_teams_to_score = self._save_in_market(
                                both_teams_to_score, data)
                        elif market == 'Double Chance':
                            double_chance = self._save_in_market(
                                double_chance, data)
        rows_dict = {'full_time_result': full_time_result,
                     'under_over': under_over,
                     'draw_no_bet': draw_no_bet,
                     'both_teams_to_score': both_teams_to_score,
                     'double_chance': double_chance}
        return rows_dict

    @staticmethod
    def _save_in_market(market, data):
        for i, v in enumerate(market):
            if v[2] == data[2]:
                data += v
                market.pop(i)
        market.append(data)
        return market

    def _parse_datetime(self, row):
        month, day, year = row[0].split(' - ')[-1].split('/')
        date = datetime.date(int(year), int(month), int(day))
        try:
            time = datetime.datetime.strptime(row[1], '%I:%M %p').time()
        except ValueError:
            if '+' in row[1]:
                row.pop(1)
            time_str = ' '.join(row[1].split(' ')[-2:])
            time = datetime.datetime.strptime(time_str, '%I:%M %p').time()
        return datetime.datetime.combine(date, time)

    def _parse_teams(self, row):
        teams, msg = [], ''
        try:  # full_time result format
            datetime.datetime.strptime(row[1], '%I:%M %p')
            index = row.index('X')
            teams_list = row[index - 2::4]
        except ValueError:
            if '+' in row[1]:
                row.pop(1)
            teams_list = row[1].split(' - ')
            teams_list[1] = ' '.join(teams_list[1].split(' ')[:-2])
        for i in teams_list:
            team = self.teams(self.country, self.league, full=True).get(i)
            teams.append(team)
            if not team:
                msg = f'{i} not in bookmaker teams table. ' + msg
        if None in teams:
            raise KeyError(msg + 'Tables need an upgrade, notify the devs.')
        return teams

    def _parse_event(self, row):
        datetime = self._parse_datetime(row)
        home_team, away_team = self._parse_teams(row)
        event = {
            'datetime': datetime,
            'country': self.country,
            'league': self.league,
            'home_team': home_team,
            'away_team': away_team,
            # 'home_goal': 0,
            # 'away_goal': 0,
        }
        return event

    def _parse_full_time_result(self, row):
        i = row.index('X')
        _1 = float(row[i - 1])
        _X = float(row[i + 1])
        _2 = float(row[i + 3])
        return {'1': _1, 'X': _X, '2': _2}

    def _parse_under_over(self, row):
        under, over = None, None
        try:
            i = row.index('Total Goals - Over/Under')
        except ValueError:
            return None
        for j, value in enumerate(row[i + 1::2]):
            if 'Over' not in value and 'Under' not in value:
                break
            if 'Under 2,5' == value:
                under = row[i + (j + 1) * 2]
            if 'Over 2,5' == value:
                over = row[i + (j + 1) * 2]
        if under is not None and over is not None:
            return {'under': under, 'over': over}
        return None

    def _parse_draw_no_bet(self, row):
        try:
            i = row.index('Draw no bet')
            _1 = float(row[i + 2])
            _2 = float(row[i + 4])
            return {'1': _1, '2': _2}
        except ValueError:
            return None

    def _parse_both_teams_to_score(self, row):
        try:
            i = row.index('Both Teams to Score')
            yes = float(row[i + 2])
            no = float(row[i + 4])
            return {'yes': yes, 'no': no}
        except (ValueError, IndexError):
            return None

    def _parse_double_chance(self, row):
        try:
            i = row.index('Double Chance')
            _1X = float(row[i + 2])
            _X2 = float(row[i + 4])
            _12 = float(row[i + 6])
            return {'1X': _1X, 'X2': _X2, '12': _12}
        except (ValueError, IndexError):
            return None

    def _market(self, rows, parse_func):
        events, odds = [], []
        for row in rows:
            events.append(self._parse_event(row))
            odds.append(getattr(self, parse_func)(row))
        assert len(events) == len(odds)
        return events, odds

    @staticmethod
    def _sort_odds(events, odds_events, odds):
        # match odds to its relative events.
        # Useful if rows are  mixed between markets
        es, oes, os = events, odds_events, odds
        odds = [os[oes.index(e)] if e in oes else None for e in es]
        return odds

    def _events_odds(self, events_only=False):
        self._odds = []
        self._request_page(events_only=events_only)
        rows_dict = self._get_rows(events_only=events_only)
        self._events, full_time_result = self._market(
            rows_dict['full_time_result'], '_parse_full_time_result')
        if events_only:
            return self._events
        under_over = self._sort_odds(
            self._events, *self._market(
                rows_dict['under_over'], '_parse_under_over'))
        draw_no_bet = self._sort_odds(
            self._events, *self._market(
                rows_dict['draw_no_bet'], '_parse_draw_no_bet'))
        both_teams_to_score = self._sort_odds(
            self._events, *self._market(
                rows_dict['both_teams_to_score'],
                '_parse_both_teams_to_score'))
        double_chance = self._sort_odds(
            self._events, *self._market(
                rows_dict['double_chance'], '_parse_double_chance'))
        for i in range(len(self._events)):
            self._odds.append({
                'full_time_result': full_time_result[i],
                'under_over': under_over[i],
                'draw_no_bet': draw_no_bet[i],
                'both_teams_to_score': both_teams_to_score[i],
                'double_chance': double_chance[i],
            })
        return self._events, self._odds

