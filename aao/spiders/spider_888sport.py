from datetime import datetime as dt
import json
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .spider import Spider


class Spider888sport(Spider):
    name = '888sport'
    base_url = 'https://www.888sport.com/'
    file_path = os.path.dirname(__file__)
    table_path = os.path.join(file_path, 'tables', f'{name}.json')
    with open(table_path) as f:
        table = json.load(f)

    def __init__(self):
        super().__init__()
        self._soccer = Soccer(self.browser, self.table)

    @property
    def soccer(self):
        return self._soccer


class Soccer(Spider888sport):

    def __init__(self, browser, table):
        self.browser = browser
        self.countries_dict = table['soccer']['countries']
        self.leagues_dict = table['soccer']['leagues']

    def _change_market(self, market):
        current_market = self.browser.find_element_by_xpath(
            '//li[@class="KambiBC-dropdown__selection"]')
        if current_market.text == market:
            return
        self.browser.execute_script("window.scrollTo(0, -100)")
        dropdown = self.browser.find_element_by_xpath(
            '//div[@class="KambiBC-mod-event-bet-offer-category-selection"]')
        dropdown_btn = dropdown.find_element_by_tag_name('header')
        time.sleep(0.5)
        dropdown_btn.click()
        dropdown.find_element_by_xpath(f'//li[text()="{market}"]').click()
        time.sleep(1)  # to improve

    def _get_rows(self):
        rows = []
        panes = self.browser.find_elements_by_xpath(
            '//div[@class="KambiBC-collapsible-container '
            'KambiBC-mod-event-group-container KambiBC-expanded"]')
        for pane in panes:
            header = pane.find_element_by_tag_name('h2').text
            if 'Live' in header:
                continue
            rows += pane.find_elements_by_tag_name('li')
        return rows

    def odds(self, country_std, league_std):
        events = []
        odds = []
        league = self.leagues_dict[country_std][league_std]
        country = self.countries_dict[country_std]
        if league is None:
            raise KeyError(f'{league} is not supported in {self.name}')

        # get the page
        self.browser.get(
            f'{self.base_url}#/filter/football/{country}/{league}')
        time.sleep(4)  # to improve

        # expands the closed panes
        close_panes = self.browser.find_elements_by_xpath(
            '//div[@class="KambiBC-collapsible-container '
            'KambiBC-mod-event-group-container"]')
        [pane.click() for pane in close_panes]

        panes = self.browser.find_elements_by_xpath(
            '//div[@class="KambiBC-collapsible-container '
            'KambiBC-mod-event-group-container KambiBC-expanded"]')

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
                    'country': country_std,
                    'league': league_std,
                    'home_team': home_team,
                    'away_team': away_team
                }
                odds.append(odd)
                events.append(event)

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

        # scrape both teams to score
        self._change_market('Both Teams To Score')
        rows = self._get_rows()
        for i, row in enumerate(rows):
            value = row.text.split('\n')
            if ':' in value[0]:
                value = [''] + value
            try:
                yes, no = float(value[7]), float(value[9])
                odds[i]['both_teams_to_score'] = {'yes': no, 'no': no}
            except IndexError:
                pass

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

        return events, odds
