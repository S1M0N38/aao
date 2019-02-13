import datetime
import re

from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from aao.spiders.spider import Spider
from aao.spiders import sports


class SpiderBet365(Spider):
    bookmaker = 'bet365'
    base_url = 'https://www.bet365.com/'

    def __init__(self, username=None, password=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._homepage()
        self._select_language()
        # if browser is in en version of the site, is no longer necessary to
        # login. If you try login in this situation, an error will be raise
        if self.base_url not in self.browser.current_url:
            self._login(username, password)
        # self._change_odds_format('Decimal')
        self._soccer = Soccer(self)

    def _homepage(self):
        self.log.debug('requesting homepage …')
        self.browser.get(self.base_url)
        self.wait.until(EC.invisibility_of_element_located((By.ID, 'dBlur')))

    def _select_language(self):
        self.log.debug('setting english lang …')
        lang = '//ul[@class="lpnm"]/li/a'
        lang_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, lang)))
        lang_btn.click()
        #   if 'cb' not in self.browser.current_url:
        #    self.wait.until(
        #        EC.invisibility_of_element_located((By.ID, 'dBlur')))
        #    lang_btn = self.wait.until(
        #        EC.element_to_be_clickable((By.XPATH, lang)))
        #    lang_btn.click()

    # Not really usefull because in account options you can specify
    # the defaut odds format
    def _change_odds_format(self, format_):
        self.log.debug('setting odds format to decimal …')
        # three formats possible: Fractional, Decimal, American. The format
        # had to be switch to 'Decimal' due to the future type conversion
        dropdown = ('//div[@class="hm-OddsDropDownSelections '
                    'hm-DropDownSelections "]')
        type_ = (f'//div[@class="hm-DropDownSelections_ContainerInner "]'
                 f'/a[text() = "{format_}"]')
        drop_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, dropdown)))
        drop_btn.click()
        self.browser.find_element_by_xpath(type_).click()

    def _login(self, username, password):
        self.log.debug(f'trying to log using {username} …')
        username_box, password_box = self.browser.find_elements_by_xpath(
            '//input[@class="hm-Login_InputField "]')
        password_box_hidden = self.browser.find_element_by_xpath(
            '//input[@class="hm-Login_InputField Hidden "]')
        submit_button = self.browser.find_element_by_class_name(
            'hm-Login_LoginBtn')
        username_box.clear()
        username_box.send_keys(username)
        password_box.click()
        password_box_hidden.clear()
        password_box_hidden.send_keys(password)
        submit_button.click()
        try:
            name_shown = 'hm-UserName_UserNameShown'
            self.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, name_shown)))
        except TimeoutException:
            raise ValueError('The username password combination is wrong.')
        self.log.debug('closing the confermation-identity pop up …')
        pop_up = 'wl-UserNotificationsPopup_Frame'
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, pop_up)))
        self.browser.switch_to.frame('messageWindow')
        button = self.browser.find_element_by_id('remindLater')
        button.click()
        self.browser.switch_to.default_content()
        elements = 'hm-HeaderModule_Link'
        self.wait.until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, elements)))
        self.log.info(f'logged in with {username}')

    @property
    def soccer(self):
        if not re.match(r'https://www\.bet365\.com/#/A[SC]/B1/',
                        self.browser.current_url):
            self.browser.get(self.base_url + '#/AS/B1/')
            self.log.debug('opening soccer page …')
        return self._soccer


class Soccer(sports.Soccer):

    def __init__(self, spider):
        super().__init__(spider)

    def _expands_country(self):
        xpath = f'//div[@class="sm-Market "]//div[text()="{self._country}"]'
        self.wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, xpath), self._country))
        country_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, xpath)))
        header = country_btn.find_element_by_xpath(
            '..').get_attribute('class')
        if header == 'sm-Market_HeaderClosed ':
            self.log.debug(f'expanding {self.country} tab …')
            country_btn.click()
        xpath = xpath + '/../..//div[@class="sm-CouponLink_Label "]'
        self.browser.find_elements_by_xpath(xpath)

    def _request_page(self):
        self.log.debug(f'requesting page {self.country} - {self.league} …')
        self.browser.get(self.base_url + '#/AS/B1/')
        try:
            self._expands_country()
            xpath = (f'//div[@class="sm-Market "]/div/div[text()='
                     f'"{self._country}"]/../..//div[@class="sm-'
                     f'CouponLink_Label " and text()="{self._league}"]')
            league_btn = self.browser.find_element_by_xpath(xpath)
            league_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, xpath)))
            league_btn.click()
        except (TimeoutException, NoSuchElementException):
            msg = f'No data found for {self.country} - {self.league}.'
            self.log.error(msg)
            raise KeyError(f'{msg} This competition does not have odds')

    def _change_market(self, market):
        markets = {'Full Time Result', 'Double Chance', 'Goals Over/Under',
                   'Both Teams to Score', 'Draw No Bet'}
        assert market in markets
        market_btn = self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'cm-CouponMarketGroup_ChangeMarket')))
        market_btn.click()
        xpath = f'//div[@class="wl-DropDown_Inner "]//div[text()="{market}"]'
        market = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        market.click()

    def _get_rows(self):
        days = {'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'}
        xpath_cols = ('//div[@class="gl-MarketGroupContainer '
                      'gl-MarketGroupContainer_HasLabels "]/div')
        xpath_rows = ('//div[@class="sl-MarketCouponFixtureLabelBase '
                      'gl-Market_General gl-Market_HasLabels "]/div')
        cols_len = len(self.browser.find_elements_by_xpath(xpath_cols))
        rows_len = len(self.browser.find_elements_by_xpath(xpath_rows))
        rows = []
        for i in range(1, rows_len + 1):
            row = []
            for j in range(1, cols_len + 1):
                xpath = xpath_cols + f'[{j}]/div[{i}]'
                value = self.browser.find_element_by_xpath(xpath).text
                if value[:3] in days:
                    date = value
                    break
                row.append(value)
            # exclude dumbs rows and live matches
            if row and len(row[0].split('\n')) == 2:
                rows.append([date] + row[0].split('\n') + row[1:])
        return rows

    def _parse_datetime(self, row):
        format_ = '%a %d %b'
        date = datetime.date.today()
        while date.strftime(format_) != row[0]:
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
            # 'home_goal': 0,
            # 'away_goal': 0,
        }
        return event

    def _parse_full_time_result(self, row):
        return {'1': float(row[3]), 'X': float(row[4]), '2': float(row[5])}

    def _parse_under_over(self, row):
        return {'under': float(row[4]), 'over': float(row[3])}

    def _parse_draw_no_bet(self, row):
        return {'1': float(row[3]), '2': float(row[4])}

    def _parse_both_teams_to_score(self, row):
        return {'yes': float(row[3]), 'no': float(row[4])}

    def _parse_double_chance(self, row):
        return {'1X': float(row[3]), 'X2': float(row[4]), '12': float(row[5])}

    def _events_full_time_result(self):
        events, full_time_result = [], []
        self._change_market('Full Time Result')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            full_time_result.append(self._parse_full_time_result(row))
        return events, full_time_result

    def _under_over(self):
        events, under_over = [], []
        self._change_market('Goals Over/Under')
        rows = self._get_rows()
        for row in rows:
            events.append(self._parse_event(row))
            under_over.append(self._parse_under_over(row))
        return events, under_over

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
        self._change_market('Both Teams to Score')
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
        self._events, full_time_result = self._events_full_time_result()
        if events_only:
            return self._events
        under_over = self._sort_odds(
            self._events, *self._under_over())
        draw_no_bet = self._sort_odds(
            self._events, *self._draw_no_bet())
        both_teams_to_score = self._sort_odds(
            self._events, *self._both_teams_to_score())
        double_chance = self._sort_odds(
            self._events, *self._double_chance())
        for i in range(len(self._events)):
            self._odds.append([
                {'full_time_result': full_time_result[i]},
                {'under_over': under_over[i]},
                {'draw_no_bet': draw_no_bet[i]},
                {'both_teams_to_score': both_teams_to_score[i]},
                {'double_chance': double_chance[i]},
            ])
        return self._events, self._odds

