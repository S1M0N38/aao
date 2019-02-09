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
    def _events_odds(self):
        pass

    def countries(self, full=False):
        countries = self.table['soccer']
        if full:
            return countries
        return list(countries)

    def leagues(self, country, full=False):
        leagues = self.countries(full=True)[country]['leagues']
        if full:
            return leagues
        return list(leagues)

    def teams(self, country, league, full=False):
        teams = self.leagues(country, full=True)[league]['teams']
        if full:
            return teams
        return list(teams.values())

    def events(self, country, league):
        pass

    def odds(self, country, league):
        pass

