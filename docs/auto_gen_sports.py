import os
from aao.spiders.tables import TABLES, BOOKMAKERS


here = os.path.abspath(os.path.dirname(__file__))


def save_file(file_name, gen_doc):
    with open(os.path.join(here, file_name), 'w') as f:
        f.write(gen_doc())

##############################################################################


def gen_table_soccer(country, country_id):
    flag = f'flag-icon flag-icon-{country_id}'
    tab = f'\n---\n#### <span class="{flag}" style="margin:6px"></span> '
    tab += f'&nbsp; &nbsp; {country}\n'
    row_0 = '| ' + '&nbsp;' * 30 + 'league' + '&nbsp;' * 30 + ' | '
    row_0 = '| ' + '&nbsp; ' * 15 + 'league' + '&nbsp; ' * 15 + ' | '
    row_0 += ' &nbsp; | '.join(BOOKMAKERS) + ' |\n'
    row_1 = '|-|' + ':-:|' * len(BOOKMAKERS) + '\n'
    tab += row_0 + row_1
    for k in TABLES['bet365']['soccer'][country]['leagues']:
        row = f'|{k}|'
        for bookmaker in BOOKMAKERS[0:3:2]:  # other bookmakers needs new format
            if TABLES[bookmaker]['soccer'][country]['leagues'][k]['teams']:
                row += '✓|-|'
            else:
                row += '-|-|'
        tab += row + '\n'
    return tab


def gen_doc_soccer():
    doc = '# Soccer\n'
    doc += gen_table_soccer('england', 'gb-eng')
    doc += gen_table_soccer('italy', 'it')
    return doc

##############################################################################


save_file('sports/soccer.md', gen_doc_soccer)
