import os

import pytest

from aao.spiders import SpiderBet365


pytestmark = pytest.mark.bet365

username = os.environ['BET365_USERNAME']
password = os.environ['BET365_PASSWORD']

COMPETIONS = [
    # country, _country, league, _league, page_name
    ['england', 'United Kingdom', 'premier_league', 'England Premier League'],
    # ['england', 'england', 'elf_championship', 'the_championship', 'The Championship'],
    ['italy', 'Italy', 'serie_a', 'Italy Serie A'],
    # ['spain', 'spain', 'la_liga', 'la_liga', 'La Liga'],
]


class TestSpider():

    @pytest.fixture()
    def spider(self):
        spider = SpiderBet365.__new__(SpiderBet365)
        super(SpiderBet365, spider).__init__()
        yield spider
        spider.quit()

    def test_homepage(self, spider):
        spider._homepage()
        xpath = '//ul[@class="lpnm"]/li/a'
        langs = spider.browser.find_elements_by_xpath(xpath)
        assert langs
        assert 'bet365' in spider.browser.current_url

    def test_select_language(self, spider):
        spider._homepage()
        spider._select_language()
        assert spider.browser.find_elements_by_class_name(
            'hm-HeaderModule_Logo')

    def test_login_correct_credentials(self, spider):
        spider._homepage()
        spider._select_language()
        if spider.base_url in spider.browser.current_url:
            return
        spider._login(username, password)
        username_in_box = spider.browser.find_element_by_class_name(
            'hm-UserName_UserNameShown')
        assert username == username_in_box.text

    def test_login_wrong_credentials(self, spider):
        spider._homepage()
        spider._select_language()
        if spider.base_url in spider.browser.current_url:
            return
        msg = 'The username password combination is wrong.'
        with pytest.raises(ValueError, match=msg):
            spider._login('foo_username', 'foo_password')

    def test_soccer(self):
        spider = SpiderBet365(username=username, password=password)
        spider.soccer
        sport = spider.browser.find_element_by_class_name(
            'sl-ClassificationHeader_ClassificationName').text
        assert sport == 'Soccer'
        spider.quit()


class TestSoccer():

    competition = COMPETIONS[0]

    @pytest.fixture(scope='module')
    def spider(self):
        spider = SpiderBet365()
        spider.soccer.country = self.competition[0]
        spider.soccer._country = self.competition[1]
        spider.soccer.league = self.competition[2]
        spider.soccer._league = self.competition[3]
        yield spider
        spider.quit()

    @pytest.mark.action
    def test_expands_country(self, spider):
        spider.soccer._expands_country()
        xpath = (f'//div[@class="sm-Market "]'
                 f'//div[text()="{spider.soccer._country}"]')
        country_btn = spider.browser.find_element_by_xpath(xpath)
        btn_status = country_btn.find_element_by_xpath(
            '..').get_attribute('class')
        assert btn_status == 'sm-Market_HeaderOpen '

    @pytest.mark.action
    def test_request_page(self, spider):
        spider.soccer._request_page()
        league = spider.browser.find_element_by_class_name(
            'cl-EnhancedDropDown').text
        assert league == spider.soccer._league

    @pytest.mark.action
    def test_request_page_no_data_found_country(self, spider):
        spider.soccer._country = 'foo country'
        with pytest.raises(KeyError, match='No data found for'):
            spider.soccer._request_page()
        spider.soccer._country = self.competition[1]

    @pytest.mark.action
    def test_request_page_no_data_found_league(self, spider):
        spider.soccer._league = 'foo league'
        with pytest.raises(KeyError, match='No data found for'):
            spider.soccer._request_page()
        spider.soccer._league = self.competition[3]

    @pytest.mark.action
    def test_change_market(self, spider):
        market = 'Double Chance'
        spider.soccer._request_page()
        spider.soccer._change_market(market)
        market_found = spider.browser.find_elements_by_class_name(
            'cm-CouponMarketGroupButton_Text')[0].text
        assert market == market_found

    @pytest.mark.action
    def test_get_rows(self, spider):
        spider.soccer._request_page()
        rows = spider.soccer._get_rows()
        assert rows

    @pytest.mark.parser
    def test_parse_datetime(self, spider):
        spider.soccer._request_page()
        rows = spider.soccer._get_rows()
        for row in rows:
            datetime_str = str(spider.soccer._parse_datetime(row))
            if row[0].isdigit():
                assert row[0] in datetime_str
            assert row[1] in datetime_str

    @pytest.mark.parser
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

    @pytest.mark.parser
    def test_parse_teams_team_not_in_table(self, spider):
        row = ['Sun 20 Jan', '14:00', 'foo_home_team v foo_away_team']
        msg = ('foo_away_team not in bookmaker teams table. '
               'foo_home_team not in bookmaker teams table. '
               'Tables need an upgrade, notify the devs.')
        with pytest.raises(KeyError, match=msg):
            spider.soccer._parse_teams(row)

    # markets

    market_funcs = ['_events_full_time_result', '_under_over', '_draw_no_bet',
                    '_both_teams_to_score', '_double_chance']

    @pytest.mark.parametrize('market_func', market_funcs)
    def test_market(self, spider, market_func):
        spider.soccer._request_page()
        events, odds = getattr(spider.soccer, market_func)()
        assert len(events) == len(odds)

    # events + odds

    @pytest.mark.action
    def test_events_odds(self, spider):
        events, odds = spider.soccer._events_odds()
        assert events
        assert odds

    @pytest.mark.action
    def test_events_odds_events_only(self, spider):
        events = spider.soccer._events_odds(events_only=True)
        assert events
