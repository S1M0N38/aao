from datetime import datetime as dt

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    NoSuchElementException, ElementNotVisibleException)

from .spider import Spider


class SpiderWilliamhill(Spider):
    name = 'williamhill'
    base_url = 'http://sports.williamhill.com/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_session()
        self._soccer = Soccer(self)

    def start_session(self):
        self.log.info('starting new session ...')
        self.homepage()
        # Sometimes appeare timezone popup, but not always
        try:
            self.select_timezone()
        except ElementNotVisibleException:
            self.log.debug('already set London timezone')

    def select_timezone(self):
        popup = self.browser.find_element_by_id('popupMain')
        popup.find_element_by_class_name('linkable').click()
        select = Select(popup.find_element_by_id('time_zone'))
        select.select_by_value("1")  # 1 -> London timezone
        popup.find_element_by_id('yesBtn').click()
        self.log.debug('set London timezone')

    def change_odds_format(self, format_: str):
        # three formats possible: ODDS(fractional), DECIMAL, AMERICAN. Format
        # had to be switch to 'Decimal' due to the future type conversion
        select = Select(self.browser.find_element_by_id('oddsSelect'))
        select.select_by_value(format_)
        self.log.debug('set odds format to decimal')

    @property
    def soccer(self):
        self.log.debug('opening soccer page ...')
        self.browser.get(
            f'{self.base_url}bet/en-gb/betting/y/5/et/Football.html')
        return self._soccer


class Soccer(SpiderWilliamhill):

    def __init__(self, other):
        self.browser = other.browser
        self.log = other.log
        self.table = other.table
        self.wait = other.wait
        self.countries_dict = self.table['soccer']['countries']
        self.leagues_dict = self.table['soccer']['leagues']

    def _country_league(self):
        table = self.browser.find_element_by_class_name('listContainer')
        try:
            page_link = table.find_element_by_xpath(
                f'//h3["{self.country}"=text()]/../ul/li/a["{self.league}"=text()]')
        except NoSuchElementException:
            msg = (f'{self.country_std} - {self.league_std} not found on '
                   f'{self.name} site, it seams that not odds are avaiable.')
            self.log.warning(msg)
            raise KeyError(msg)
        self.log.debug(f'requesting page {self.country_std}, {self.league_std}')
        page_link.click()

    def _matches(self) -> tuple:
        events = []
        odds = []
        events_id = []
        self._country_league()
        self.change_odds_format('DECIMAL')
        self.log.info(f'* scraping: {self.country_std} - {self.league_std} *')
        # parse events and full time result
        full_time_result = self.browser.find_element_by_xpath(
            '//table[@class="tableData"]//span'
            '["90 Minutes"=text()]/../../../../tbody')
        rows = full_time_result.find_elements_by_class_name('rowOdd')
        for row in rows:
            events_id.append(row.get_attribute('id').split('_')[2])
            data = row.find_elements_by_tag_name('td')
            try:
                timestamp = int(data[0].find_element_by_tag_name(
                    'span').get_attribute('id').split(':')[2])
                datetime = dt.fromtimestamp(timestamp)
            except NoSuchElementException:
                timestamp = None
                datetime = None
            home_team, away_team = data[2].text.split('   v   ')
            _1, _X, _2 = data[4].text, data[5].text, data[6].text
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
        # parse double chance
        self.browser.find_element_by_xpath(
            '//a[contains(text(), "\tDouble Chance")]').click()
        double_chance = self.browser.find_element_by_xpath(
            '//table[@class="tableData"]//span'
            '["Double Chance"=text()]/../../../../tbody')
        rows = double_chance.find_elements_by_class_name('rowOdd')
        for row in rows:
            data = row.find_elements_by_tag_name('td')
            i = events_id.index(row.get_attribute('id').split('_')[2])
            _1X, _X2, _12 = data[4].text, data[5].text, data[6].text
            odds[i]['double_chance'] = {
                '1X': float(_1X), 'X2': float(_X2), '12': float(_12)}
        self.log.debug(' * got double chance odds')
        # parse draw no bet
        self.browser.find_element_by_xpath(
            '//a[contains(text(), "\tDraw No Bet")]').click()
        draw_no_bet = self.browser.find_element_by_xpath(
            '//table[@class="tableData"]//span'
            '["Draw No Bet"=text()]/../../../../tbody')
        rows = draw_no_bet.find_elements_by_class_name('rowOdd')
        for row in rows:
            data = row.find_elements_by_tag_name('td')
            i = events_id.index(row.get_attribute('id').split('_')[2])
            _1, _2 = data[3].text, data[5].text
            odds[i]['draw_no_bet'] = {
                '1': float(_1), '2': float(_2)}
        self.log.debug(' * got draw no bet odds')
        # parse both team to score
        self.browser.find_element_by_xpath(
            '//a[contains(text(), "\tBoth Teams To Score")]').click()
        both_team_to_score = self.browser.find_element_by_xpath(
            '//table[@class="tableData"]//span[contains(text(),'
            ' "\tBoth Teams To Score")]/../../../../tbody')
        rows = both_team_to_score.find_elements_by_class_name('rowOdd')
        for row in rows:
            data = row.find_elements_by_tag_name('td')
            i = events_id.index(row.get_attribute('id').split('_')[2])
            yes, no = data[4].text, data[5].text
            odds[i]['both_team_to_score'] = {
                'yes': float(yes), 'no': float(no)}
        self.log.debug(' * got both teams to score odds')
        # parse under over 2.5
        self.browser.find_element_by_xpath(
            '//a[contains(text(), '
            '"\tTotal Match Goals Over/Under 2.5 Goals")]').click()
        under_over_multiple = self.browser.find_elements_by_xpath(
            '//table[@class="tableData"]//span[contains(text(),'
            ' "Total Match Goals Over/Under 2.5 Goals")]/../../../../tbody')
        for under_over in under_over_multiple:
            rows = under_over.find_elements_by_class_name('rowOdd')
            for i, row in enumerate(rows[::2]):
                data = rows[i+1].find_elements_by_tag_name('td')
                i = row.find_element_by_tag_name('td')
                i = events_id.index(i.get_attribute('id').split('_')[2])
                u, o = data[3].text, data[5].text
                odds[i]['under_over_2.5'] = {
                    'under': float(u), 'over': float(o)}
        self.log.debug(' * got under/over 2.5 odds')
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
