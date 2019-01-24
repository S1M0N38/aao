import os

import pytest

from aao.spiders import Spider888sport


PROXY = os.environ['PROXY']
COMPETITIONS = [
    # country, _country, league, _league, page_name
    ['england', 'england', 'premier_league', 'premier_league', 'Premier League'],
    ['england', 'england', 'elf_championship', 'the_championship', 'The Championship'],
    ['italy', 'italy', 'serie_a', 'serie_a', 'Serie A'],
    ['spain', 'spain', 'la_liga', 'la_liga', 'La Liga'],
    ]


class TestSpider():

    def test_soccer(self):
        pass


class TestSoccer():

    competition = COMPETITIONS[2]

    @pytest.fixture(scope='module')
    def spider(self):
        spider = Spider888sport()  # (proxy=PROXY)
        spider.soccer.country = self.competition[0]
        spider.soccer._country = self.competition[1]
        spider.soccer.league = self.competition[2]
        spider.soccer._league = self.competition[3]
        yield spider
        spider.quit()

    @pytest.mark.action
    def test_request_page(self, spider):
        spider.soccer._request_page()
        xpath = '//li[@class="KambiBC-term KambiBC-js-slider-item"]'
        league = spider.browser.find_element_by_xpath(xpath).text
        assert league == self.competition[4]

    @pytest.mark.action
    def test_request_page_no_data_found(self, spider):
        with pytest.raises(KeyError, match='No data found for'):
            spider.soccer._country = 'foo_country'
            spider.soccer._league = 'foo_league'
            spider.soccer._request_page()
            xpath = '//div[@class="KambiBC-event-groups"]'
            msg = spider.browser.find_element_by_xpath(xpath).text
            assert msg == 'There are currently no match events available.'
        spider.soccer._country = self.competition[1]
        spider.soccer._league = self.competition[3]

    @pytest.mark.action
    def test_change_market(self, spider):
        spider.soccer._request_page()
        spider.soccer._change_market('Draw No Bet')
        xpath = '//li[@class="KambiBC-dropdown__selection"]'
        market = spider.browser.find_element_by_xpath(xpath).text
        assert market == 'Draw No Bet'

    @pytest.mark.action
    def test_change_market_same_market(self, spider):
        spider.soccer._request_page()
        spider.soccer._change_market('Match & Total Goals')
        xpath = '//li[@class="KambiBC-dropdown__selection"]'
        market = spider.browser.find_element_by_xpath(xpath).text
        assert market == 'Match & Total Goals'

    @pytest.mark.action
    def test_expands_panes(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        xpath = ('//div[@class="KambiBC-collapsible-container '
                 'KambiBC-mod-event-group-container"]')
        panes_close = spider.browser.find_elements_by_xpath(xpath)
        assert not panes_close

    @pytest.mark.action
    def test_get_rows(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        rows = spider.soccer._get_rows()
        assert rows

    # parse

    @pytest.mark.parser
    def test_parse_datetime(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        rows = spider.soccer._get_rows()
        for row in rows:
            datetime_str = str(spider.soccer._parse_datetime(row))
            if row[0].isdigit():
                assert row[0] in datetime_str
            assert row[1] in datetime_str

    @pytest.mark.parser
    def test_parse_teams(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        rows = spider.soccer._get_rows()
        teams = spider.soccer.teams(
            spider.soccer.country, spider.soccer.league, full=True)
        for row in rows:
            home_team, away_team = spider.soccer._parse_teams(row)
            assert home_team in teams.values() and row[2] in teams
            assert away_team in teams.values() and row[3] in teams

    @pytest.mark.parser
    def test_parse_teams_team_not_in_table(self, spider):
        row = ['Sat', '18:30', 'foo_home_team', 'foo_away_team']
        msg = ('foo_away_team not in bookmaker teams table. '
               'foo_home_team not in bookmaker teams table. '
               'Tables need an upgrade, notify the devs.')
        with pytest.raises(KeyError, match=msg):
            home_team, away_team = spider.soccer._parse_teams(row)

    # markets

    @pytest.mark.market
    def test_events_full_time_result_under_over(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        data = spider.soccer._events_full_time_result_under_over()
        events, full_time_result, under_over = data
        assert len(events) == len(full_time_result) == len(under_over)

    @pytest.mark.market
    def test_draw_no_bet(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        data = spider.soccer._draw_no_bet()
        events, draw_no_bet = data
        assert len(events) == len(draw_no_bet)

    @pytest.mark.market
    def test_both_teams_to_score(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        data = spider.soccer._both_teams_to_score()
        events, both_teams_to_score = data
        assert len(events) == len(both_teams_to_score)

    @pytest.mark.market
    def test_double_chance(self, spider):
        spider.soccer._request_page()
        spider.soccer._expands_panes()
        data = spider.soccer._double_chance()
        events, double_chance = data
        assert len(events) == len(double_chance)

    # events + odds

    @pytest.mark.action
    def test_events_odds(self, spider):
        events, odds = spider.soccer._events_odds()
        assert events
        assert odds
#        for e, o in zip(events, odds):
#            print(e)
#            print(o)
#            print()

    @pytest.mark.action
    def test_events_odds_events_only(self, spider):
        events = spider.soccer._events_odds(events_only=True)
        assert events

