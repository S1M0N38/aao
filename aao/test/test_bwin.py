import unittest

from aao.spiders.spider_bwin import SpiderBwin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

LOG_LEVEL = 'CRITICAL'


class SpiderTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.s = SpiderBwin(log_level_console=LOG_LEVEL)

    @classmethod
    def tearDownClass(self):
        self.s.quit()

    def test_soccer(self):
        pass


class SoccerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.s = SpiderBwin(log_level_console=LOG_LEVEL)
        # country
        self.country_not_exists = 'this_country_does_not_exixts'
        self.country_null = 'test_country_null'
        self.country_foo = 'test_country_foo'
        self.country_std = 'italy'
        self.country = 'italy'
        # league
        self.league_not_exists = '999'  # remenber bwin store league as ids
        self.league_null = 'test_league_null'
        self.league_foo = 'test_league_foo'
        self.league_std = 'serie_a'
        self.league = '42'
        # page request params
        self.wrong_page_num = 999
        self.market_id_not_supported = ('25', '10', '1')
        self.market_ids = ('25', '31', '190', '261', '359')

    @classmethod
    def tearDownClass(self):
        self.s.quit()

    def test_country_not_exists(self):
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.country_not_exists, self.league_std)
        msg = f'{self.country_not_exists} not found in {self.s.name} table'
        self.assertIn(msg, str(context.exception))

    def test_league_not_exists(self):
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.country_std, self.league_not_exists)
        msg = f'{self.league_not_exists} not found in {self.s.name} table'
        self.assertIn(msg, str(context.exception))

    def test_country_not_supported(self):
        # the country appear in spider table but the value is null
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.country_null, self.league_std)
        msg = f'{self.country_null} not supported in {self.s.name}'
        self.assertIn(msg, str(context.exception))

    def test_league_not_supported(self):
        # the league appear in spider table but the value is null
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.country_foo, self.league_null)
        msg = f'{self.league_null} not supported in {self.s.name}'
        self.assertIn(msg, str(context.exception))

    def test_reuqest_page_wrong_league_or_wrong_page_num(self):
        # page number is too big (out of index) so no odds are avaiable.
        self.s.soccer.league = self.league
        self.s.soccer.league_std = self.league_std
        with self.assertRaises(KeyError) as context:
            self.s.soccer._request_page(self.market_ids, self.wrong_page_num)
        msg = f'no data found for {self.league_std} on page {self.wrong_page_num}'
        self.assertIn(msg, str(context.exception))

    def test_request_page_market_id_not_supported(self):
        self.s.soccer.league = self.league
        with self.assertRaises(KeyError) as context:
            self.s.soccer._request_page(self.market_id_not_supported, 0)
        msg = (f'is not supported. Supported market_id are '
               f'{list(self.s.soccer.market_ids)}')
        self.assertIn(msg, str(context.exception))

    def test_max_page_num(self):
        self.s.soccer.league = self.league
        max_page_num = self.s.soccer._max_page()
        self.assertGreaterEqual(max_page_num, 0)

    def test_odds_right(self):
        events, odds = self.s.soccer.odds(self.country_std, self.league_std)
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))
