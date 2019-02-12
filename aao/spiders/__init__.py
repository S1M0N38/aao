import importlib

package = 'aao.spiders.bookmakers'

SpiderBet365 = importlib.import_module(
    '.bet365', package).SpiderBet365
SpiderBwin = importlib.import_module(
    '.bwin', package).SpiderBwin
Spider888sport = importlib.import_module(
    '.888sport', package).Spider888sport
SpiderWilliamhill = importlib.import_module(
    '.williamhill', package).SpiderWilliamhill

spiders = {
    'bet365': SpiderBet365,
    'bwin': SpiderBwin,
    '888sport': Spider888sport,
    'williamhill': SpiderWilliamhill,
}
