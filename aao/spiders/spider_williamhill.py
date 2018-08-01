from datetime import datetime as dt

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .spider import Spider


class SpiderWilliamhill(Spider):
    name = 'williamhill'
    base_url = 'http://sports.williamhill.com/betting/en-gb'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_session()
        self._soccer = Soccer(self)

    def start_session(self):
        self.log.info('starting new session ...')
        self.homepage()

    def change_odds_format(self, format_: str):
        # three formats possible: Fraction, Decimal, American. Format
        # had to be switch to 'Decimal' due to the future type conversion
        xpath_drop = '//a[text() = "Odds Format "]'
        drop = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath_drop)))
        drop.click()
        xpath_format = (f'//li[@class="subheader__dropdown__item"]/a/'
                        f'span[text() = "{format_}"]/..')
        format_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath_format)))
        format_btn.click()
        self.log.debug(f'set odds format to {format_}')

    @property
    def soccer(self):
        return self._soccer


class Soccer(SpiderWilliamhill):

    def __init__(self, other):
        self.browser = other.browser
        self.log = other.log
        self.table = other.table
        self.wait = other.wait
        self.countries_dict = self.table['soccer']['countries']
        self.leagues_dict = self.table['soccer']['leagues']

    def _request_page(self, url):
        self.browser.get(url)
        self.change_odds_format('Decimal')
        try:
            self.wait.until(EC.visibility_of_all_elements_located(
                (By.XPATH, '//div[@data-test-id="events-group"]')))
        except TimeoutException:
            msg = f'no data found for {self.league_std} for this market'
            self.log.error(msg)
            raise KeyError(f'{msg}. It seems this league does not have odds ')

    def _matches(self) -> tuple:
        events = []
        odds = []
        url = f'{self.base_url}/football/competitions/{self.league}'
        self._request_page(url)
        self.log.debug(f'requesting page {self.country_std}, {self.league_std}')
        self.log.info(f'* scraping: {self.country_std} - {self.league_std} *')

        # events and full time result
        table = self.wait.until(
            EC.visibility_of_element_located((By.ID, 'football')))
        days = table.find_elements_by_xpath(
            '//div[@data-test-id="events-group"'
            'and contains(div, "90 Minutes")]')
        for day in days:
            date = day.find_element_by_tag_name('span').text.strip('\n')
            rows = day.find_elements_by_tag_name('article')
            for row in rows:
                _time = row.find_element_by_class_name(
                    'sp-o-market__clock').text
                teams = row.find_element_by_class_name(
                    'sp-o-market__title').text
                home_team, away_team = teams.split(' v ')
                odds_btn = row.find_elements_by_tag_name('button')
                _1, _X, _2 = [o.text for o in odds_btn]
                dt_str = ' '.join([str(dt.now().year), date, _time])
                datetime = dt.strptime(dt_str, '%Y %a %b %d %H:%M')
                timestamp = int(dt.timestamp(datetime))
                event = {
                    'timestamp': timestamp,
                    'datetime': datetime,
                    'country': self.country_std,
                    'league': self.league_std,
                    'home_team': home_team,
                    'away_team': away_team
                }
                odd = {
                    'full_time_result': {
                        '1': float(_1),
                        'X': float(_X),
                        '2': float(_2)
                    }
                }
                events.append(event)
                odds.append(odd)
        self.log.debug(' * got events data')
        self.log.debug(' * got 1 x 2 odds')

        # get link for other market
        markets_links = self.browser.find_elements_by_xpath(
            '//div[@data-test-id="carousel"]//a[@href]')
        url = 'http://sports.williamhill.com'
        links = [link.get_attribute('href') for link in markets_links]

        def find_event_index(row):
            teams = row.find_element_by_class_name(
                'sp-o-market__title').text
            home_team, away_team = teams.split(' v ')
            for i, e in enumerate(events):
                if e['home_team'] == home_team and \
                   e['away_team'] == away_team:
                    return i

        # both teams to score
        self._request_page(links[1])
        table = self.wait.until(
            EC.visibility_of_element_located((By.ID, 'football')))
        days = table.find_elements_by_xpath(
            '//div[@data-test-id="events-group"'
            'and contains(div, "Both Teams To Score")]')
        for day in days:
            rows = day.find_elements_by_tag_name('article')
            for row in rows:
                i = find_event_index(row)
                odds_btn = row.find_elements_by_tag_name('button')
                yes, no = [o.text for o in odds_btn]
                odds[i]['both_teams_to_score'] = {
                    'yes': float(yes), 'no': float(no)}
        self.log.debug(' * got both teams to score odds')

        # under over 2.5
        self._request_page(links[3])
        table = self.wait.until(
            EC.visibility_of_element_located((By.ID, 'football')))
        days = table.find_elements_by_xpath(
            '//div[@data-test-id="events-group"'
            'and contains(div, "Total Match Goals Over/Under 2.5 Goals")]')
        for day in days:
            rows = day.find_elements_by_tag_name('article')
            for row in rows:
                i = find_event_index(row)
                odds_btn = row.find_elements_by_tag_name('button')
                under, over = [o.text for o in odds_btn]
                odds[i]['under_over'] = {
                    'under': float(under), 'over': float(over)}
        self.log.debug(' * got under/over 2.5 odds')

        # double chance
        self._request_page(links[5])
        table = self.wait.until(
            EC.visibility_of_element_located((By.ID, 'football')))
        days = table.find_elements_by_xpath(
            '//div[@data-test-id="events-group"'
            'and contains(div, "Double Chance")]')
        for day in days:
            rows = day.find_elements_by_tag_name('article')
            for row in rows:
                i = find_event_index(row)
                odds_btn = row.find_elements_by_tag_name('button')
                _1X, _X2, _12 = [o.text for o in odds_btn]
                odds[i]['double_chance'] = {'1X': _1X, 'X2': _X2, '12': _12}
        self.log.debug(' * got double chance odds')

        # draw no bet NOT AVAIABLE

        return events, odds

    def odds(self, country_std: str, league_std: str) -> tuple:
        msg_to_docs = 'Check the docs for a list of supported competitions'
        try:
            self.country_std = country_std
            self.country = self.countries_dict[country_std]
        except KeyError:
            msg = f'{country_std} not found in {self.name} table'
            self.log.error(msg)
            raise KeyError(f'{msg}. {msg_to_docs}')
        if self.country is None:
            msg = f'{country_std} not supported in {self.name}'
            self.log.error(msg)
            raise KeyError(f'{msg}. {msg_to_docs}')
        try:
            self.league_std = league_std
            self.league = self.leagues_dict[country_std][league_std]
        except KeyError:
            msg = f'{country_std} - {league_std} not found in {self.name} table'
            self.log.error(msg)
            raise KeyError(f'{msg}. {msg_to_docs}')
        if self.league is None:
            msg = f'{country_std} - {league_std} not supported in {self.name}'
            self.log.error(msg)
            raise KeyError(f'{msg}. {msg_to_docs}')
        events, odds = self._matches()
        return events, odds
