from datetime import datetime as dt

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .spider import Spider


class SpiderBet365(Spider):
    name = 'bet365'
    base_url = 'https://www.bet365.com/'

    def __init__(self, username, password, *args, **kwargs):
        super().__init__(username, password, *args, **kwargs)
        self.start_session()
        self._soccer = Soccer(self)

    def start_session(self):
        self.log.info('starting new session ...')
        self.homepage()
        lang = '//ul[@class="lpnm"]/li/a'
        self.wait.until(EC.invisibility_of_element_located((By.ID, 'dBlur')))
        lang_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, lang)))
        lang_btn.click()
        if 'lng' not in self.browser.current_url:
            self.wait.until(EC.invisibility_of_element_located((By.ID, 'dBlur')))
            lang_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, lang)))
            lang_btn.click()
        self.log.debug('set english language')
        self.login()
        self.change_odds_format('Decimal')

    def change_odds_format(self, format_):
        # three formats possible: Fractional, Decimal, American. The format
        # had to be switch to 'Decimal' due to the future type conversion
        dropdown = '//div[@class="hm-OddsDropDownSelections hm-DropDownSelections "]'
        type_ = (f'//div[@class="hm-DropDownSelections_ContainerInner "]'
                 f'/a[text() = "{format_}"]')
        drop_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, dropdown)))
        drop_btn.click()
        self.log.debug('set odds format to decimal')
        self.browser.find_element_by_xpath(type_).click()

    def login(self):
        self.log.debug(f'trying to log using {self.username} ...')
        username_box, password_box = self.browser.find_elements_by_xpath(
            '//input[@class="hm-Login_InputField "]')
        password_box_hidden = self.browser.find_element_by_xpath(
            '//input[@class="hm-Login_InputField Hidden "]')
        submit_button = self.browser.find_element_by_class_name(
            'hm-Login_LoginBtn')
        username_box.clear()
        username_box.send_keys(self.username)
        password_box.click()
        password_box_hidden.clear()
        password_box_hidden.send_keys(self.password)
        submit_button.click()
        name_shown = 'hm-UserName_UserNameShown'
        pop_up = 'wl-UserPopups_FrameContainer'
        self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, name_shown)))
        self.log.debug('closing the confermation-identity pop up ...')
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, pop_up)))
        self.browser.get(self.base_url)
        self.log.info(f'logged in with {self.username}')

    @property
    def soccer(self):
        xpath = '//div[contains(@class, "wn-Classification ")][text()="Soccer"]'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        soccer_btn = self.browser.find_element_by_xpath(xpath)
        soccer_btn.click()
        sport_click = self.browser.find_element_by_class_name(
            'wl-ClassificationHeader_ClassificationName ')
        if sport_click.text == 'Soccer':
            self.log.debug('opening soccer page ...')
            return self._soccer
        self.soccer


class Soccer(SpiderBet365):

    def __init__(self, other):
        self.browser = other.browser
        self.log = other.log
        self.table = other.table
        self.wait = other.wait
        self.countries_dict = self.table['soccer']['countries']
        self.leagues_dict = self.table['soccer']['leagues']

    def _country(self):
        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.CLASS_NAME, 'fm-FooterModule_Logo')))
            xpath = f'//div[@class="sm-Market "]//div[text()="{self.country}"]'
            country = self.browser.find_element_by_xpath(xpath)
            self.wait.until(EC.visibility_of(country))
            self.wait.until(EC.text_to_be_present_in_element(
                (By.XPATH, xpath), self.country))
            country = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, xpath)))
            header = country.find_element_by_xpath('..').get_attribute('class')
            if header == 'sm-Market_HeaderClosed ':
                self.log.debug(f'expanding {self.country_std} tab ...')
                country.click()
            self.wait.until(EC.visibility_of(country))
        except NoSuchElementException:
            msg = (f'{self.country_std} not found on {self.name} site, it '
                   f'seams that not odds are avaiable for this country.')
            self.log.warning(msg)
            raise KeyError(msg)

    def _league(self):
        try:
            xpath = (f'//div[@class="sm-Market "]//div[text()="{self.country}"]'
                     f'/../..//div[text()="{self.league}"]')
            league = self.browser.find_element_by_xpath(xpath)
            league = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            league.click()
            self.log.debug(f'opened {self.league_std} page.')
        except NoSuchElementException:
            msg = (f'{self.league_std} not found on {self.name} site, it '
                   f'seams that not odds are avaiable for this country.')
            self.log.warning(msg)
            raise KeyError(msg)

    def _events(self) -> list:
        events = []
        days = ('Sun ', 'Mon ', 'Tue ', 'Wed ', 'Thu ', 'Fri ', 'Sat ')
        rows = self.browser.find_elements_by_xpath(
            '//div[@class="sl-MarketCouponFixtureLabelBase '
            'gl-Market_General gl-Market_HasLabels "]/div')
        for r in rows:
            if r.text.startswith(days):
                date = r.text
                continue
            _time, teams = r.text.split('\n')
            home_team, away_team = teams.split(' v ')
            dt_str = ' '.join([str(dt.now().year), date, _time])
            datetime = dt.strptime(dt_str, '%Y %a %d %b  %H:%M')
            timestamp = int(dt.timestamp(datetime))
            event = {
                'timestamp': timestamp,
                'datetime': datetime,
                'country': self.country_std,
                'league': self.league_std,
                'home_team': home_team,
                'away_team': away_team,
            }
            events.append(event)
        self.log.debug(' * got events data')
        return events

    def _markets(self, type_) -> list:
        market_btn = self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'cm-CouponMarketGroup_ChangeMarket')))
        market_btn.click()
        xpath = f'//div[@class="wl-DropDown_Inner "]//div[text()="{type_}"]'
        market = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        market.click()
        xpath_odds = '//span[@class="gl-ParticipantOddsOnly_Odds"]'
        o = self.browser.find_elements_by_xpath(xpath_odds)
        return [float(i.text) for i in o]

    def _matches(self) -> tuple:
        self.log.info(f'* scraping: {self.country_std} - {self.league_std} *')
        # scrape events data
        events = self._events()
        # scrape markets data
        k = len(events)
        odds = [{} for i in range(k)]
        o = self._markets('Full Time Result')
        for i, _1, _X, _2 in zip(range(k), o[:], o[k:-k], o[-k:]):
            odds[i]['full_time_result'] = {'1': _1, 'X': _X, '2': _2}
        self.log.debug(' * got 1 x 2 odds')
        o = self._markets('Double Chance')
        for i, _1X, _X2, _12 in zip(range(k), o[:], o[k:-k], o[-k:]):
            odds[i]['double_chance'] = {'1X': _1X, 'X2': _X2, '12': _12}
        self.log.debug(' * got double chance odds')
        o = self._markets('Goals Over/Under')
        for i, over, under in zip(range(k), o[:k], o[k:]):
            odds[i]['under_over_2.5'] = {'under': under, 'over': over}
        self.log.debug(' * got under/over 2.5 odds')
        o = self._markets('Both Teams to Score')
        for i, yes, no in zip(range(k), o[:k], o[k:]):
            odds[i]['both_teams_to_score'] = {'yes': yes, 'no': no}
        self.log.debug(' * got both teams to score odds')
        o = self._markets('Draw No Bet')
        for i, _1, _2 in zip(range(k), o[:k], o[k:]):
            odds[i]['draw_no_bet'] = {'1': _1, '2': _2}
        self.log.debug(' * got draw no bet odds')
        self.log.info('* finished the scrape *')
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
        self._country()
        self._league()
        events, odds = self._matches()
        return events, odds


# TODO add here other sport class
