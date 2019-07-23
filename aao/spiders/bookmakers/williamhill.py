import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from aao.spiders.spider import Spider
from aao.spiders import sports


class SpiderWilliamhill(Spider):
    bookmaker = 'williamhill'
    base_url = 'http://sports.williamhill.com/betting/en-gb'

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
        url = f'{self.base_url}/football/competitions/{self._league}/matches'
        self.browser.get(url)
        locator = (By.XPATH, '//div[@data-test-id="events-group"]')
        try:
            self.wait.until(EC.visibility_of_all_elements_located(locator))
        except TimeoutException:
            msg = f'No data found for {self.country} - {self.league}.'
            self.log.error(msg)
            raise KeyError(f'{msg} This competition does not have odds')

    def _change_market(self, market):
        markets = {'Match Betting', 'Both Teams To Score', 'Double Chance',
                   'Total Match Goals Over/Under 2.5 Goals'}
        assert market in markets
        locator = (By.XPATH, f'//li[@class="css-xnumgp"]//a[.="{market}"]')
        market_btn = self.wait.until(EC.element_to_be_clickable(locator))
        market_btn.click()
        locator = (By.CLASS_NAME, 'sp-betbutton')
        self.wait.until(EC.visibility_of_all_elements_located(locator))

    def _get_rows(self):
        days = {'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'}
        xpath = ('//div[@id="football"]//*[self::header or self::article]'
                 '[contains(@class, "sp-o-market sp-o-market--default")]')
        rows = []
        for row in self.browser.find_elements_by_xpath(xpath):
            values = row.text.split('\n')
            if values[0][:3] in days:
                date = values[0]
                continue
            rows.append([date] + values)
        return rows

    def _parse_datetime(self, row):
        format_ = '%a %d %b'
        date = datetime.date.today()
        # in some version the format is ['Sat, 09 Feb', ...]
        while date.strftime(format_) != row[0].replace(',', ''):
            date += datetime.timedelta(1)
        time = datetime.datetime.strptime(row[1], '%H:%M').time()
        return datetime.datetime.combine(date, time)

    def _parse_teams(self, row):
        teams, msg = [], ''
        for i in row[2].split(' v '):
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
        }
        return event

    def _parse_full_time_result(self, row):
        return {'1': self.odd2decimal(row[3]),
                'X': self.odd2decimal(row[4]),
                '2': self.odd2decimal(row[5])}

    def _parse_under_over(self, row):
        return {'under': self.odd2decimal(row[4]),
                'over': self.odd2decimal(row[3])}

    def _parse_both_teams_to_score(self, row):
        return {'yes': self.odd2decimal(row[3]),
                'no': self.odd2decimal(row[4])}

    def _parse_double_chance(self, row):
        return {'1X': self.odd2decimal(row[3]),
                'X2': self.odd2decimal(row[4]),
                '12': self.odd2decimal(row[5])}

    def _events_full_time_result(self):
        events, full_time_result = [], []
        self._change_market('Match Betting')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            full_time_result.append(self._parse_full_time_result(row))
        return events, full_time_result

    def _under_over(self):
        events, under_over = [], []
        self._change_market('Total Match Goals Over/Under 2.5 Goals')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            under_over.append(self._parse_under_over(row))
        return events, under_over

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
        # (this way also handle when events > odds_events)
        sort_odds = []
        for e in events:
            if e in odds_events:
                sort_odds.append(odds[odds_events.index(e)])
            else:
                sort_odds.append(None)
        return sort_odds

    def _events_odds(self, events_only=False):
        self._odds = []
        self._request_page()
        self._events, full_time_result = self._events_full_time_result()
        if events_only:
            return self._events
        under_over = self._sort_odds(
            self._events, *self._under_over())
        both_teams_to_score = self._sort_odds(
            self._events, *self._both_teams_to_score())
        double_chance = self._sort_odds(
            self._events, *self._double_chance())
        for i in range(len(self._events)):
            self._odds.append({
                'full_time_result': full_time_result[i],
                'under_over': under_over[i],
                'draw_no_bet': None,  # doesn't exists
                'both_teams_to_score': both_teams_to_score[i],
                'double_chance': double_chance[i],
            })
        return self._events, self._odds
