import unittest

from aao.spiders.spider_888sport import Spider888sport

LOG_LEVEL = 'CRITICAL'
HEADLESS = False


class SpiderTest(unittest.TestCase):
    def setUp(self):
        self.s = Spider888sport(log_level_console=LOG_LEVEL, headless=HEADLESS)

    def tearDown(self):
        self.s.browser.quit()

    def test_soccer(self):
        pass


class SoccerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.s = Spider888sport(log_level_console=LOG_LEVEL, headless=HEADLESS)
        # country
        self.country_not_exists = 'this_country_does_not_exixts'
        self.country_null = 'test_country_null'
        self.country_foo = 'test_country_foo'
        self.country_std = 'world_cup_2018'
        self.country = 'world_cup_2018'
        # league
        self.league_not_exists = 'this_league_does_not_exixts'
        self.league_null = 'test_league_null'
        self.league_foo = 'test_league_foo'
        self.league_std = 'world_cup_2018'
        self.league = 'world_cup_2018'

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

    def test_request_page(self):
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.country_foo, self.league_foo)
        msg = f'no data found for {self.league_foo}'
        self.assertIn(msg, str(context.exception))
        msg = self.s.browser.find_element_by_class_name(
            'KambiBC-event-groups').text
        self.assertIn('There are currently no match events available.', msg)

    def test_odds_right(self):
        events, odds = self.s.soccer.odds(self.country_std, self.league_std)
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))
