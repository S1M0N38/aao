import pytest

from aao.spiders import SpiderWilliamhill


pytestmark = pytest.mark.williamhill

COMPETITIONS = [
    # country, _country, league, _league, page_name
    ['england', 'england', 'premier_league', 'English-Premier-League', 'English Premier League'],
    ['italy', 'italy', 'serie_a', 'Italian-Serie-A', 'Italian Serie A'],
    ['spain', 'spain', 'la_liga', 'Spanish-La-Liga-Primera', 'Spanish La Liga Primera'],
]


class TestSpider():

    def test_soccer(self):
        pass


class TestSoccer():

    competition = COMPETITIONS[0]

    @pytest.fixture(scope='class')
    def spider(self):
        spider = SpiderWilliamhill()
        spider.soccer.country = self.competition[0]
        spider.soccer._country = self.competition[1]
        spider.soccer.league = self.competition[2]
        spider.soccer._league = self.competition[3]
        yield spider
        spider.quit()

    def test_request_page(self, spider):
        spider.soccer._request_page()
        league = spider.browser.find_element_by_class_name('header-title')
        assert league.text == self.competition[4]

    def test_request_page_no_data_found(self, spider):
        with pytest.raises(KeyError, match='No data found for'):
            spider.soccer._country = 'foo_country'
            spider.soccer._league = 'foo_league'
            spider.soccer._request_page()
        header = spider.browser.find_element_by_class_name('header-title')
        assert header.text == 'Competitions'
        spider.soccer._country = self.competition[1]
        spider.soccer._league = self.competition[3]

    def test_change_market(self, spider):
        spider.soccer._request_page()
        spider.soccer._change_market('Double Chance')
        xpath = '//div[@class="sp-o-market__title"]/b'
        market = spider.browser.find_element_by_xpath(xpath).text
        assert market == 'Double Chance'

    def test_get_rows(self, spider):
        spider.soccer._request_page()
        rows = spider.soccer._get_rows()
        assert rows

    # parse

    def test_parse_datetime(self, spider):
        spider.soccer._request_page()
        rows = spider.soccer._get_rows()
        for row in rows:
            datetime_str = str(spider.soccer._parse_datetime(row))
            if row[0][4:6].isdigit():
                assert row[0][4:6] in datetime_str
            assert row[1] in datetime_str

    def test_parse_teams(self, spider):
        spider.soccer._request_page()
        rows = spider.soccer._get_rows()
        teams = spider.soccer.teams(
            spider.soccer.country, spider.soccer.league, full=True)
        for row in rows:
            home_team, away_team = spider.soccer._parse_teams(row)
            row[2], row[3] = row[2].split(' v ')
            assert home_team in teams.values() and row[2] in teams
            assert away_team in teams.values() and row[3] in teams

    def test_parse_teams_team_not_in_table(self, spider):
        row = ['Sun 20 Jan', '14:00', 'foo_home_team v foo_away_team']
        msg = ('foo_away_team not in bookmaker teams table. '
               'foo_home_team not in bookmaker teams table. '
               'Tables need an upgrade, notify the devs.')
        with pytest.raises(KeyError, match=msg):
            spider.soccer._parse_teams(row)

    # markets

    market_funcs = ['_events_full_time_result', '_under_over',
                    '_both_teams_to_score', '_double_chance']

    @pytest.mark.parametrize('market_func', market_funcs)
    def test_market(self, spider, market_func):
        spider.soccer._request_page()
        events, odds = getattr(spider.soccer, market_func)()
        assert len(events) == len(odds)

    # events + odds

    def test_events_odds(self, spider):
        events, odds = spider.soccer._events_odds()
        assert events
        assert odds

    def test_events_odds_events_only(self, spider):
        events = spider.soccer._events_odds(events_only=True)
        assert events
