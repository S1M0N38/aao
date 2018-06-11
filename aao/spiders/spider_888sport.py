from datetime import datetime as dt

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .spider import Spider


class Spider888sport(Spider):
    name = '888sport'
    base_url = 'https://www.888sport.com/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._soccer = Soccer(self)

    @property
    def soccer(self):
        return self._soccer


class Soccer(Spider888sport):

    def __init__(self, other):
        self.browser = other.browser
        self.log = other.log
        self.table = other.table
        self.wait = other.wait
        self.countries_dict = self.table['soccer']['countries']
        self.leagues_dict = self.table['soccer']['leagues']

    def _request_page(self):
        self.log.debug(f'requesting page {self.country_std}, {self.league_std}')
        url = f'{self.base_url}#/filter/football/{self.country}/'
        if url == self.browser.current_url:
            self.browser.refresh()
        if self.league != '':
            url += self.league
        self.browser.get(url)
        try:
            self.wait.until(EC.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'KambiBC-mod-event-group-header__title-inner')))
        except TimeoutException:
            msg = f'no data found for {self.league_std}'
            self.log.error(msg)
            raise KeyError(f'{msg}. It seems this league does not have odds ')

    def _change_market(self, market: str):
        current_market = self.browser.find_element_by_xpath(
            '//li[@class="KambiBC-dropdown__selection"]')
        if current_market.text == market:
            return
        self.browser.execute_script("window.scrollTo(0, -100)")
        dropdown = self.browser.find_element_by_xpath(
            '//div[@class="KambiBC-mod-event-bet-offer-category-selection"]')
        self.wait.until(EC.visibility_of(dropdown))
        self.wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'header')))
        dropdown_btn = dropdown.find_element_by_tag_name('header')
        dropdown_btn.click()
        dropdown.find_element_by_xpath(f'//li[text()="{market}"]').click()
        self.wait.until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'KambiBC-event-item__event-wrapper')))

    def _get_rows(self) -> list:
        rows = []
        panes = self.browser.find_elements_by_xpath(
            '//div[@class="KambiBC-collapsible-container '
            'KambiBC-mod-event-group-container KambiBC-expanded"]')
        for pane in panes:
            header = pane.find_element_by_tag_name('h2').text
            if 'Live' in header:
                continue
            rows += pane.find_elements_by_tag_name('li')
        self.wait.until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'KambiBC-event-item__link')))
        return rows

    def _matches(self) -> tuple:
        events = []
        odds = []
        # get the page
        self._request_page()
        # expands closed panes
        self.log.debug(f'opening closed panes ...')
        close_panes = self.browser.find_elements_by_xpath(
            '//div[@class="KambiBC-collapsible-container '
            'KambiBC-mod-event-group-container"]')
        [pane.click() for pane in close_panes]
        panes = self.browser.find_elements_by_xpath(
            '//div[@class="KambiBC-collapsible-container '
            'KambiBC-mod-event-group-container KambiBC-expanded"]')
        self.log.info(f'* scraping: {self.country_std} - {self.league_std} *')
        # parse events, full time result and under over
        for pane in panes:
            header = pane.find_element_by_tag_name('h2').text
            if 'Live' in header:
                continue
            _, date = header.split(' \n')
            year = str(dt.now().year)  # pay attention on 01/01
            if date.isdigit():
                year = date
                date = _
            rows = pane.find_elements_by_tag_name('li')
            for row in rows[2:]:
                value = row.text.split('\n')
                home_team, away_team = value[2], value[3]
                odd = {}
                try:
                    _time = value[1]
                    dt_str = f'{date} {year} {_time}'
                    datetime = dt.strptime(dt_str, '%d %B %Y %H:%M')
                    timestamp = int(dt.timestamp(datetime))
                except (IndexError, ValueError):  # countdown started
                    value = [''] + value
                    datetime, timestamp = None, None
                if value[4] != 'Live':  # Live column is missing
                    value = [''] + value
                try:
                    _1 = float(value[7])
                    _X = float(value[9])
                    _2 = float(value[11])
                    odd['full_time_result'] = {'1': _1, 'X': _X, '2': _2}
                except IndexError:  # full time result  doesn't exists
                    _1, _X, _2 = None, None, None
                try:
                    over, under = float(value[14]), float(value[17])
                    odd['under_over'] = {'under': under, 'over': over}
                except IndexError:  # under over doesn't exists
                    over, under = None, None
                event = {
                    'timestamp': timestamp,
                    'datetime': datetime,
                    'country': self.country_std,
                    'league': self.league_std,
                    'home_team': home_team,
                    'away_team': away_team
                }
                odds.append(odd)
                events.append(event)
        self.log.debug(' * got events data')
        self.log.debug(' * got 1 x 2 odds')
        self.log.debug(' * got under/over 2.5 odds')
        # scrape draw no bet
        self._change_market('Draw No Bet')
        rows = self._get_rows()
        for i, row in enumerate(rows):
            value = row.text.split('\n')
            if ':' in value[0]:
                value = [''] + value
            try:
                _1, _2 = float(value[7]), float(value[9])
                odds[i]['draw_no_bet'] = {'1': _1, '2': _2}
            except IndexError:
                pass
        self.log.debug(' * got draw no bet odds')
        # scrape both teams to score
        self._change_market('Both Teams To Score')
        rows = self._get_rows()
        for i, row in enumerate(rows):
            value = row.text.split('\n')
            if ':' in value[0]:
                value = [''] + value
            try:
                yes, no = float(value[7]), float(value[9])
                odds[i]['both_teams_to_score'] = {'yes': yes, 'no': no}
            except IndexError:
                pass
        self.log.debug(' * got both teams to score odds')
        # scrape double chance
        self._change_market('Double Chance')
        rows = self._get_rows()
        for i, row in enumerate(rows):
            value = row.text.split('\n')
            if ':' in value[0]:
                value = [''] + value
            try:
                _1X = float(value[7])
                _12 = float(value[9])
                _X2 = float(value[11])
                odds[i]['double_chance'] = {'1X': _1X, 'X2': _X2, '12': _12}
            except IndexError:
                pass
        self.log.debug(' * got double chance odds')
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
