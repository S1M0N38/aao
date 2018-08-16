import collections
import json
import os


BOOKMAKERS = ['bet365', 'bwin', '888sport', 'williamhill']
FLAGS = {
    None
}


def table(bookmaker):
    here = os.path.dirname(__file__)
    table_path = os.path.join(here, f'{bookmaker}.json')
    with open(table_path) as f:
        table = json.load(f)
    return table


TABLES = {b: table(b) for b in BOOKMAKERS}


# Soccer
def countries(bookmaker):
    countries_list = sorted(TABLES[bookmaker]['soccer']['countries'].keys())
    countries_list.remove('test_country_foo')
    countries_list.remove('test_country_null')
    return countries_list


COUNTRIES = countries(BOOKMAKERS[0])
assert all(countries(b) == COUNTRIES for b in BOOKMAKERS)


def leagues(bookmaker):
    leagues_dict = collections.OrderedDict()
    for country in COUNTRIES:
        leagues_dict[country] = sorted(
            TABLES[bookmaker]['soccer']['leagues'][country].keys())
    return leagues_dict


LEAGUES = leagues(BOOKMAKERS[0])
assert all(leagues(b) == LEAGUES for b in BOOKMAKERS)


# Other Sport
