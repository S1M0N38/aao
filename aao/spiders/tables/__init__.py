import json
import os


def table(bookmaker):
    here = os.path.dirname(__file__)
    table_path = os.path.join(here, f'{bookmaker}.json')
    with open(table_path) as f:
        table = json.load(f)
    return table


BOOKMAKERS = ['bet365', 'bwin', '888sport', 'williamhill']

TABLES = {b: table(b) for b in BOOKMAKERS}

