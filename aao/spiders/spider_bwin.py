from datetime import datetime as dt

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .spider import Spider


class SpiderBwin(Spider):
    name = 'bwin'
    base_url = 'https://sports.bwin.com/en/sports#'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._soccer = Soccer(self)

    @property
    def soccer(self):
        return self._soccer


class Soccer(SpiderBwin):
    sport_id = '4'
    market_ids = {
        '25': 'events_and_full_time_result',
        '31': 'under_over',
        '190': 'double_chance',
        '261': 'both_teams_to_score',
        '359': 'draw_no_bet'
    }

    def __init__(self, other):
        self.browser = other.browser
        self.log = other.log
        self.table = other.table
        self.wait = other.wait
        self.countries_dict = self.table['soccer']['countries']
        self.leagues_dict = self.table['soccer']['leagues']

    def _request_page(self, markets: list, page_num: int):
        if page_num < 0:
            page_num = 0
        for id_ in markets:
            if id_ not in self.market_ids:
                msg = f'market {id_} is not supported'
                self.log.error(msg)
                raise KeyError(
                    f'{msg}. Supported market_id are {list(self.market_ids)}')
        markets_str = ','.join(markets)
        url = (f'{self.base_url}sportId={self.sport_id}&leagueIds='
               f'{self.league}&categoryIds={markets_str}&page={page_num}')
        self.log.debug(
            f'requesting page markets:{markets_str} page_num:{page_num}')
        self.browser.get(url)
        self.wait.until(
            EC.invisibility_of_element_located((By.ID, 'ajax-spinner')))
        if page_num != 0:
            try:
                xpath = (f'//a[@class="active-page-link"]'
                         f'[text()="{page_num + 1}"]')
                self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                msg = f'no data found for {self.league_std} on page {page_num}'
                self.log.error(msg)
                raise KeyError((f'{msg}. It seems league does not have odds or'
                                f' page number is out of index.'))

    def _max_page(self) -> int:
        self._request_page(['25', '359', '31', '190', '261'], 0)
        try:
            num = int(self.browser.find_element_by_class_name(
                'markets-pager__pages-count'
                ).text.split('| ')[1].split(' ')[0])
        except NoSuchElementException:
            num = 0
        return num

    def _parse_events_and_full_time_result(self):
        xpath = ('//div[@class="marketboard-event-group__item-container '
                 'marketboard-event-group__item-container--level-2"]')
        data = self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, xpath)))
        days = data.find_elements_by_class_name(
            'marketboard-event-group__item--sub-group')
        for day in days:
            date = day.find_element_by_tag_name('h2').text.split(' - ')[1]
            rows = day.find_elements_by_class_name(
                'marketboard-event-group__item--event')
            for row in rows:
                class_name = 'marketboard-event-without-header__market-time'
                try:
                    self.wait.until(EC.visibility_of_element_located(
                        (By.CLASS_NAME, class_name))).text
                    time_str = row.find_element_by_class_name(class_name).text
                except TimeoutException:
                    msg = f'no data found for {self.league_std}'
                    self.log.error(msg)
                    raise KeyError(f'{msg}. It seems league does not have odds')
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
                self._events.append(event)
                self._odds.append(odd)

    def _parse_markets(self):
        data = self.browser.find_elements_by_xpath(
            ('//div[@class="marketboard-event-group__item-container '
             'marketboard-event-group__item-container--level-2"]'))
        # iterate through differnt markets, data[0] == events & 1x2
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
                for i, event in enumerate(self._events):
                    if event["home_team"] == home_team and \
                       event["away_team"] == away_team:
                        index_order = i
                        break
                rows = match.find_elements_by_tag_name('div')
                header_row = None
                for i, row in enumerate(rows):
                    if row.get_attribute('class') == \
                       'marketboard-event-with-header__market-name':
                        header_row = row.text
                    if 'Draw no bet' == header_row:
                        _, _1, _, _2 = rows[i+1].text.split('\n')
                        self._odds[index_order]['draw_no_bet'] = {
                            '1': float(_1), '2': float(_2)}
                        break
                    if 'Both Teams to Score' == header_row:
                        _, yes, _, no = rows[i+1].text.split('\n')
                        self._odds[index_order]['both_teams_to_score'] = {
                            'yes': float(yes), 'no': float(no)}
                        break
                    if 'Double Chance' == header_row:
                        _, _1X, _, _X2, _, _12 = rows[i+1].text.split('\n')
                        self._odds[index_order]['double_chance'] = {
                            '1X': float(_1X), 'X2': float(_X2), '12': float(_12)}
                        break
                    if 'Total Goals - Over/Under' == header_row:
                        if ("Over 2,5" and "Under 2,5") in row.text:
                            _, o, _, u = row.text.split('\n')
                            self._odds[index_order]['under_over'] = {
                                'under': float(u), 'over': float(o)}
                            break

    def _matches(self) -> tuple:
        self.log.info(f'* scraping: {self.country_std}, {self.league_std} *')
        self._events = []
        self._odds = []
        # scrape events data and 1 x 2 odds
        self._request_page(['25'], 0)
        self._parse_events_and_full_time_result()
        self.log.debug(' * got events data')
        self.log.debug(' * got 1 x 2 odds')
        # scrape odds data
        max_page_num = self._max_page()
        self.log.debug(f'got total page number -> {max_page_num}')
        for page_num in range(max_page_num):
            self._request_page(['25', '359', '31', '190', '261'], page_num)
            self._parse_markets()
            self.log.debug(f' * got markets odds, page {page_num}')
        self.log.info('* finished the scrape *')
        return self._events, self._odds

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
