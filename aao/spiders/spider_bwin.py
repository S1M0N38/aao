from datetime import datetime as dt
import json
import os
import time

from .spider import Spider


class SpiderBwin(Spider):
    name = 'bwin'
    base_url = 'https://sports.bwin.com/en/sports#'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._soccer = Soccer(self.browser, self.log, self.table)

    @property
    def soccer(self):
        return self._soccer


class Soccer(SpiderBwin):
    sportId = '4'

    def __init__(self, browser, log, table):
        self.browser = browser
        self.log = log
        self.leagues_dict = table['soccer']['leagues']

    def odds(self, country, league):
        events = []
        odds = []
        leagueId = self.leagues_dict[country][league]
        if leagueId is None:
            msg = f'{league} is not supported in {self.name}'
            self.log.warning(msg)
            raise KeyError(f'{msg}. Check the docs for a list of supported leagues')

        def request_page(markets, page_num):
            url = (f'{self.base_url}sportId={self.sportId}&leagueIds='
                   f'{leagueId}&categoryIds={markets}&page={page_num}')
            self.browser.get(url)

        def max_page():
            request_page('25,359,31,190,261', 0)
            try:
                num = int(self.browser.find_element_by_class_name(
                    'markets-pager__pages-count'
                    ).text.split('| ')[1].split(' ')[0])
            except NoSuchElementException:
                num = 0
            return num

        # scrape data for events and full_time_result
        def events_and_full_time_result():
            data = self.browser.find_element_by_xpath(
                ('//div[@class="marketboard-event-group__item-container '
                 'marketboard-event-group__item-container--level-2"]'))
            days = data.find_elements_by_class_name(
                'marketboard-event-group__item--sub-group')
            for day in days:
                date = day.find_element_by_tag_name('h2').text.split(' - ')[1]
                rows = day.find_elements_by_class_name(
                    'marketboard-event-group__item--event')
                for row in rows:
                    time_str = row.find_element_by_class_name(
                        'marketboard-event-without-header__market-time').text
                    dt_str = f'{date} {time_str}'
                    datetime = dt.strptime(dt_str, '%m/%d/%Y %I:%M %p')
                    timestamp = int(dt.timestamp(datetime))
                    right, middle, left = row.find_elements_by_tag_name('td')
                    home_team, _1 = right.text.split('\n')
                    _, _X = middle.text.split('\n')
                    away_team, _2 = left.text.split('\n')
                    event = {
                        'timestamp': timestamp,
                        'datetime': datetime,
                        'country': country,
                        'league': league,
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

        # scrape odds form other markets
        def parse_markets():
            home_teams = [i['home_team'] for i in events]
            away_teams = [i['away_team'] for i in events]
            data = self.browser.find_elements_by_xpath(
                ('//div[@class="marketboard-event-group__item-container '
                 'marketboard-event-group__item-container--level-2"]'))

            # iterate through differnt markets
            for category in data[1:]:
                matches = category.find_elements_by_class_name(
                    'marketboard-event-with-header')
                for match in matches:

                    # extract home_team and away_team
                    mat_header = match.find_element_by_class_name(
                        'marketboard-event-with-header__header')
                    home_team, away_team = mat_header.text.split(' - ')
                    away_team = ' '.join(away_team.split(' ')[:-2])

                    # finds index of the events row
                    home_team_i = home_teams.index(home_team)
                    away_team_i = away_teams.index(away_team)
                    if home_team_i != away_team_i:
                        raise ValueError(
                            f'home_team_index {home_team_i} and '
                            f'away_team_index {away_team_i} are not the same')

                    rows = match.find_elements_by_tag_name('div')
                    header_row = None

                    for i, row in enumerate(rows):

                        if row.get_attribute('class') == \
                           'marketboard-event-with-header__market-name':
                            header_row = row.text
                        if 'Draw no bet' == header_row:
                            _, _1, _, _2 = rows[i+1].text.split('\n')
                            odds[home_team_i]['draw_no_bet'] = {
                                '1': float(_1), '2': float(_2)}
                            break
                        if 'Both Teams to Score' == header_row:
                            _, yes, _, no = rows[i+1].text.split('\n')
                            odds[home_team_i]['both_team_to_score'] = {
                                'yes': float(yes), 'no': float(no)}
                            break
                        if 'Double Chance' == header_row:
                            _, _1X, _, _X2, _, _12 = rows[i+1].text.split('\n')
                            odds[home_team_i]['double_chance'] = {
                                '1X': float(_1X), 'X2': float(_X2), '12': float(_12)}
                            break
                        if 'Total Goals - Over/Under' == header_row:
                            if ("Over 2,5" and "Under 2,5") in row.text:
                                _, o, _, u = row.text.split('\n')
                                odds[home_team_i]['under_over_2.5'] = {
                                    'under': float(u), 'over': float(o)}
                                break

        # 25 -> events and full_time_result
        self.log.info(f'* start scraping: {country}, {league} *')
        request_page('25', 0)
        events_and_full_time_result()
        self.log.debug(f' * got events and full time result')

        # 31 -> under_over_2.5
        # 359 -> draw_no_bet
        # 190 -> double_chance
        # 261 -> both_team_to_score
        max_page_num = max_page()
        self.log.debug(f'got total page number -> {max_page_num}')
        for i in range(max_page_num):
            request_page('25,359,31,190,261', i)
            time.sleep(3)
            parse_markets()
            self.log.debug(f' * got markets odds, page {i}')

        return events, odds
