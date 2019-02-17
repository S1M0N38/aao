from abc import ABC, abstractmethod


class Sport():
    def __init__(self, spider):
        self.spider = spider

    def __getattr__(self, name):
        return getattr(self.spider, name)


class Soccer(ABC, Sport):

    def __init__(self, spider):
        super().__init__(spider)

    @abstractmethod
    def _events_odds(self, events_only):
        pass

    def countries(self, full=False):
        countries = self.table['soccer']
        if full:
            return countries
        return list(countries)

    def leagues(self, country, full=False):
        try:
            leagues = self.countries(full=True)[country]['leagues']
        except KeyError:
            raise KeyError(
                f'{country} is not supported by this spider. '
                f'Take a look at the docs for a list of supported countries')
        if full:
            return leagues
        return list(leagues)

    def teams(self, country, league, full=False):
        try:
            teams = self.leagues(country, full=True)[league]['teams']
        except KeyError:
            raise KeyError(
                f'{league} is not supported by this spider. '
                f'Take a look at the docs for a list of supported leagues')
        if full:
            return teams
        return list(teams.values())

    def _setattr_competiton(self, country, league):
        _country = self.soccer.countries(full=True)[country]['name']
        _league = self.soccer.leagues(country, full=True)[league]['name']
        self.soccer._country, self.soccer._league = _country, _league
        self.soccer.country, self.soccer.league = country, league

    def events(self, country, league):
        self._setattr_competiton(country, league)
        events = self.soccer._events_odds(events_only=True)
        return events

    def odds(self, country, league):
        self._setattr_competiton(country, league)
        events, odds = self.soccer._events_odds()
        return events, odds
