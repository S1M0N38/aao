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
    row_0 = '| ' + '&nbsp; ' * 15 + 'league' + '&nbsp; ' * 15 + ' | '
    row_0 += ' | '.join(BOOKMAKERS) + ' |\n'
    row_1 = '|-|' + ':-:|' * len(BOOKMAKERS) + '\n'
    tab += row_0 + row_1
    for k in TABLES['bet365']['soccer'][country]['leagues']:
        row = f'|{k}|'
        for bookmaker in BOOKMAKERS:
            if TABLES[bookmaker]['soccer'][country]['leagues'][k]['teams']:
                row += '✓|'
            else:
                row += '-|'
        tab += row + '\n'
    return tab


def gen_doc_soccer():
    doc = '# Soccer\n'
    doc += gen_table_soccer('england', 'gb-eng')
    doc += gen_table_soccer('france', 'fr')
    doc += gen_table_soccer('germany', 'de')
    doc += gen_table_soccer('italy', 'it')
    doc += gen_table_soccer('spain', 'es')
    return doc

##############################################################################


save_file('soccer.md', gen_doc_soccer)
