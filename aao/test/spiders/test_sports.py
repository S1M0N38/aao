import pytest

from aao.spiders import spiders


pytestmark = pytest.mark.sports


class TestSport():
    """Nothing to test. """
    pass


class TestSoccer():
    """Test the Soccer ABC across all bookmakers. """

    @pytest.fixture(scope='class', params=spiders.values())
    def spider(self, request):
        s = request.param()
        yield s
        s.quit()

    competitions = {
        'england': 'premier_league',
        'italy': 'serie_a',
        'spain': 'la_liga',
    }

    def test_countries(self, spider):
        countries = spider.soccer.countries()
        assert set(self.competitions.keys()) <= set(countries)
        assert isinstance(countries, list)

    def test_countries_full(self, spider):
        countries = spider.soccer.countries(full=True)
        assert set(self.competitions.keys()) <= set(countries.keys())
        assert isinstance(countries, dict)

    @pytest.mark.parametrize('country', competitions.keys())
    def test_leagues(self, spider, country):
        leagues = spider.soccer.leagues(country)
        assert self.competitions[country] in leagues
        assert isinstance(leagues, list)

    @pytest.mark.parametrize('country', competitions.keys())
    def test_leagues_full(self, spider, country):
        leagues = spider.soccer.leagues(country, full=True)
        assert self.competitions[country] in leagues.keys()
        assert isinstance(leagues, dict)

    def test_league_not_supported(self, spider):
        country = 'foo_country'
        with pytest.raises(KeyError, match=f'{country} is not supported *'):
            spider.soccer.leagues(country)

    @pytest.mark.parametrize('country,league', competitions.items())
    def test_teams(self, spider, country, league):
        teams = spider.soccer.teams(country, league)
        assert isinstance(teams, list)

    @pytest.mark.parametrize('country,league', competitions.items())
    def test_teams_full(self, spider, country, league):
        teams = spider.soccer.teams(country, league, full=True)
        assert isinstance(teams, dict)

    def test_teams_not_supported(self, spider):
        country, league = 'serie_a', 'foo_league'
        with pytest.raises(KeyError, match=f'{league} is not supported *'):
            spider.soccer.teams(country, league)

    @pytest.mark.parametrize('country,league', competitions.items())
    def test_setattr_competiton(self, spider, country, league):
        spider.soccer._setattr_competiton(country, league)
        assert spider.soccer._country
        assert spider.soccer.country
        assert spider.soccer._league
        assert spider.soccer.league

    @pytest.mark.parametrize(
        'country,league', [next(iter(competitions.items()))])
    def test_events(self, spider, country, league):
        events = spider.soccer.events(country, league)
        assert isinstance(events, list)
        assert events

    @pytest.mark.parametrize(
        'country,league', [next(iter(competitions.items()))])
    def test_odds(self, spider, country, league):
        events, odds = spider.soccer.odds(country, league)
        assert isinstance(events, list)
        assert events
        assert isinstance(odds, list)
        assert odds
