import pytest

from aao.spiders import SpiderBwin


pytestmark = pytest.mark.bwin

COMPETITIONS = [
    # country, _country, league, _league, page_name
    ['england', 'england', 'premier_league', '46', 'Premier League Betting Odds'],
    ['england', 'england', 'elf_championship', '3890', 'Championship Betting Odds'],
    ['italy', 'italy', 'serie_a', '42', 'Serie A Odds'],
    ['spain', 'spain', 'la_liga', '16108', 'La Liga Odds'],
]


class TestSpider():

    def test_soccer(self):
        pass


class TestSoccer():

    competition = COMPETITIONS[0]

    @pytest.fixture(scope='module')
    def spider(self):
        spider = SpiderBwin()
        spider.soccer.country = self.competition[0]
        spider.soccer._country = self.competition[1]
        spider.soccer.league = self.competition[2]
        spider.soccer._league = self.competition[3]
        yield spider
        spider.quit()

    @pytest.fixture(scope='module')
    def rows_dict(self, spider):
        spider.soccer._request_page()
        rows_dict = spider.soccer._get_rows()
        yield rows_dict

    @pytest.mark.parametrize('page_num', [0, 1])
    def test_request_page_0(self, spider, page_num):
        spider.soccer._request_page(page=page_num)
        class_name = 'sports-info-header__header'
        league = spider.browser.find_element_by_class_name(class_name).text
        assert league == self.competition[4]
        xpath = f'//li[@class="page-link" and contains(.,"{page_num + 1}")]/a'
        page_element = spider.browser.find_element_by_xpath(xpath)
        assert page_element.get_attribute('class') == 'active-page-link'

    def test_request_page_only_events(self, spider):
        spider.soccer._request_page(events_only=True)
        class_name = 'sports-info-header__header'
        league = spider.browser.find_element_by_class_name(class_name).text
        assert league == self.competition[4]
        assert not ('25,359,31,190,261' in spider.browser.current_url)

    def test_page_number(self, spider):
        spider.soccer._request_page()
        page_number = spider.soccer._page_number()
        assert page_number > 1

    def test_page_number_not_found(self, spider):
        spider.soccer._request_page(events_only=True)
        page_number = spider.soccer._page_number()
        assert page_number == 0

    def test_request_page_no_data_found(self, spider):
        with pytest.raises(KeyError, match='No data found for'):
            spider.soccer._country = 'foo_country'
            spider.soccer._league = '213'
            spider.soccer._request_page()
            msg = spider.browser.find_element_by_class_name(
                'content-message').text
            assert msg == 'The selected offer is currently not available.'
        spider.soccer._country = self.competition[1]
        spider.soccer._league = self.competition[3]

    def test_get_rows(self, rows_dict):
        assert rows_dict

    # parse

    def test_parse_datetime(self, spider):
        spider.soccer._request_page(events_only=True)
        rows_dict = spider.soccer._get_rows(events_only=True)
        rows = rows_dict['full_time_result']
        for row in rows:
            datetime_str = str(spider.soccer._parse_datetime(row))
            month, day, year = row[0].split(' - ')[-1].split('/')
            date = '-'.join([year, month.zfill(2), day.zfill(2)])
            assert date in datetime_str

    def test_parse_teams(self, spider):
        spider.soccer._request_page(events_only=True)
        rows_dict = spider.soccer._get_rows(events_only=True)
        rows = rows_dict['full_time_result']
        teams = spider.soccer.teams(
            spider.soccer.country, spider.soccer.league, full=True)
        for row in rows:
            home_team, away_team = spider.soccer._parse_teams(row)
            i = row.index('X')
            assert home_team in teams.values() and row[i - 2] in teams
            assert away_team in teams.values() and row[i + 2] in teams

    def test_parse_teams_team_not_in_table(self, spider):
        row = ['Wednesday - 1/30/2019', '9:00 PM', '+106',
               'foo_home_team', '1.65', 'X', '3.90', 'foo_away_team', '5.25']
        msg = ('foo_away_team not in bookmaker teams table. '
               'foo_home_team not in bookmaker teams table. '
               'Tables need an upgrade, notify the devs.')
        with pytest.raises(KeyError, match=msg):
            home_team, away_team = spider.soccer._parse_teams(row)

    # markets

    odds_types = ['full_time_result', 'under_over', 'draw_no_bet',
                  'both_teams_to_score', 'double_chance']

    @pytest.mark.parametrize('odds_type', odds_types)
    def test_market(self, spider, rows_dict, odds_type):
        events, odds = spider.soccer._market(
            rows_dict[odds_type], f'_parse_{odds_type}')
        assert len(events) == len(odds)

    # events + odds

    def test_events_odds(self, spider):
        events, odds = spider.soccer._events_odds()
        assert events
        assert odds
        # for e, o in zip(events, odds):
        #     print(e)
        #     print(o)
        #     print()

    def test_events_odds_events_only(self, spider):
        events = spider.soccer._events_odds(events_only=True)
        assert events

