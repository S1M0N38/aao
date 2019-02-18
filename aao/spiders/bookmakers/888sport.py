import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from aao.spiders.spider import Spider
from aao.spiders import sports


class Spider888sport(Spider):
    bookmaker = '888sport'
    base_url = 'https://www.888sport.com/'

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

    def _request_page(self):
        self.log.debug(f'requesting page {self.country} - {self.league} …')
        url = (f'{self.base_url}#/filter/football/'
               f'{self._country}/{self._league}')
        if url == self.browser.current_url:
            self.browser.refresh()
        self.browser.get(url)
        class_name = 'KambiBC-mod-event-group-header__title-inner'
        locator = (By.CLASS_NAME, class_name)
        try:
            self.wait.until(EC.visibility_of_all_elements_located(locator))
        except TimeoutException:
            msg = f'No data found for {self.country} - {self.league}.'
            self.log.error(msg)
            raise KeyError(f'{msg} This competition does not have odds')

    def _change_market(self, market):
        xpath = '//li[@class="KambiBC-dropdown__selection"]'
        current_market = self.browser.find_element_by_xpath(xpath)
        if current_market.text == market:
            return
        self.browser.execute_script("window.scrollTo(0, -10000)")
        xpath = ('//div[@class='
                 '"KambiBC-mod-event-bet-offer-category-selection"]')
        dropdown = self.browser.find_element_by_xpath(xpath)
        self.wait.until(EC.visibility_of(dropdown))
        locator = (By.TAG_NAME, 'header')
        self.wait.until(EC.element_to_be_clickable(locator))
        dropdown_btn = dropdown.find_element_by_tag_name('header')
        dropdown_btn.click()
        dropdown.find_element_by_xpath(f'//li[text()="{market}"]').click()
        xpath = '//li[@class="KambiBC-dropdown__selection"]'
        locator = (By.XPATH, xpath)
        self.wait.until(EC.text_to_be_present_in_element(locator, market))

    def _expands_panes(self):
        """Some panes can be closed, to read data they must be open."""
        self.log.debug('expanding panes …')
        xpath = ('//div[@class="KambiBC-collapsible-container '
                 'KambiBC-mod-event-group-container"]')
        panes = self.browser.find_elements_by_xpath(xpath)
        [pane.click() for pane in panes]
        self.browser.execute_script("window.scrollTo(0, -10000)")

    def _get_rows(self):
        xpath = ('//header[not(contains(., "Live"))]/..'
                 '//div[@class="KambiBC-event-item__event-wrapper"]')
        rows = self.browser.find_elements_by_xpath(xpath)
        rows = [row.text.split('\n') for row in rows]
        return rows

    def _parse_datetime(self, row):
        if row[0] in {'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'}:
            format_ = '%a'
        else:
            row[0] = ' '.join(row[0].split(' ')[:2])
            # at the and of the year, also appear the new yer in row[0]
            format_ = '%-e %b'
        date = datetime.date.today()
        while date.strftime(format_) != row[0]:
            date += datetime.timedelta(1)
        time = datetime.datetime.strptime(row[1], '%H:%M').time()
        return datetime.datetime.combine(date, time)

    def _parse_teams(self, row):
        teams, msg = [], ''
        for i in range(2, 4):
            team = self.teams(self.country, self.league, full=True).get(row[i])
            teams.append(team)
            if not team:
                msg = f'{row[i]} not in bookmaker teams table. ' + msg
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
        i = row.index('Draw')
        _1 = float(row[i - 1])
        _X = float(row[i + 1])
        _2 = float(row[i + 3])
        return {'1': _1, 'X': _X, '2': _2}

    def _parse_under_over(self, row):
        i = row.index('Under')
        if row[i + 1] != '2.5' or row[i - 2] != '2.5':
            return None
        under = float(row[i + 2])
        over = float(row[i - 1])
        return {'under': under, 'over': over}

    def _parse_draw_no_bet(self, row):
        home_team = row[2]
        try:
            row = row[4:]
            i = row.index(home_team)
            _1 = float(row[i + 1])
            _2 = float(row[i + 3])
            return {'1': _1, '2': _2}
        except (ValueError, IndexError):
            return None

    def _parse_both_teams_to_score(self, row):
        try:
            i = row.index('No')
            yes = float(row[i - 1])
            no = float(row[i + 1])
            return {'yes': yes, 'no': no}
        except (ValueError, IndexError):
            return None

    def _parse_double_chance(self, row):
        try:
            i = row.index('1X')
            _1X = float(row[i + 1])
            _X2 = float(row[i + 5])
            _12 = float(row[i + 3])
            return {'1X': _1X, 'X2': _X2, '12': _12}
        except (ValueError, IndexError):
            return None

    def _events_full_time_result_under_over(self):
        events, full_time_result, under_over = [], [], []
        self._change_market('Match & Total Goals')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            full_time_result.append(self._parse_full_time_result(row))
            under_over.append(self._parse_under_over(row))
        return events, full_time_result, under_over

    def _draw_no_bet(self):
        events, draw_no_bet = [], []
        self._change_market('Draw No Bet')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            draw_no_bet.append(self._parse_draw_no_bet(row))
        return events, draw_no_bet

    def _both_teams_to_score(self):
        events, both_teams_to_score = [], []
        self._change_market('Both Teams To Score')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            both_teams_to_score.append(self._parse_both_teams_to_score(row))
        return events, both_teams_to_score

    def _double_chance(self):
        events, double_chance = [], []
        self._change_market('Double Chance')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            double_chance.append(self._parse_double_chance(row))
        return events, double_chance

    @staticmethod
    def _sort_odds(events, odds_events, odds):
        # match odds to its relative events.
        # Useful if rows are mixed between markets
        keys = [odds_events.index(e) for e in events]
        odds = [odds[k] for k in keys]
        return odds

    def _events_odds(self, events_only=False):
        self._odds = []
        self._request_page()
        self._expands_panes()
        self._events, *data = self._events_full_time_result_under_over()
        if events_only:
            return self._events
        full_time_result, under_over = data
        draw_no_bet = self._sort_odds(
            self._events, *self._draw_no_bet())
        both_teams_to_score = self._sort_odds(
            self._events, *self._both_teams_to_score())
        double_chance = self._sort_odds(
            self._events, *self._double_chance())
        for i in range(len(self._events)):
            self._odds.append({
                'full_time_result': full_time_result[i],
                'under_over': under_over[i],
                'draw_no_bet': draw_no_bet[i],
                'both_teams_to_score': both_teams_to_score[i],
                'double_chance': double_chance[i],
            })
        return self._events, self._odds

