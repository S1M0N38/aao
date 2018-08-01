import unittest

from aao.spiders.spider_williamhill import SpiderWilliamhill


class SpiderTest(unittest.TestCase):
    headless = False
    log_level = 'CRITICAL'
    proxy = None

    @classmethod
    def setUpClass(self):
        self.s = SpiderWilliamhill(log_level_console=self.log_level,
                                   headless=self.headless,
                                   proxy=self.proxy)

    @classmethod
    def tearDownClass(self):
        self.s.quit()

    def test_change_odds_format(self):
        self.s.change_odds_format('American')
        format_selected = self.s.browser.find_element_by_class_name(
            'odds-format__toggle').get_attribute('data-selected-format')
        self.assertEqual('american', format_selected)

    def test_soccer(self):
        pass


class SoccerTest(unittest.TestCase):
    headless = False
    log_level = 'CRITICAL'
    proxy = None

    @classmethod
    def setUpClass(self):
        self.s = SpiderWilliamhill(log_level_console=self.log_level,
                                   headless=self.headless,
                                   proxy=self.proxy)
        # country
        self.country_not_exists = 'this_country_does_not_exixts'
        self.country_null = 'test_country_null'
        self.country_foo = 'test_country_foo'
        self.country_std = 'england'
        self.country = 'england'
        # league
        self.league_not_exists = 'this_league_does_not_exixts'
        self.league_null = 'test_league_null'
        self.league_foo = 'test_league_foo'
        self.league_std = 'premier_league'
        self.league = 'English-Premier-League'

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

    def test_country_league_not_found(self):
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.country_foo, self.league_foo)
        msg = f'no data found for {self.league_foo} for this market'
        self.assertIn(msg, str(context.exception))

    def test_odds_right(self):
        events, odds = self.s.soccer.odds(self.country_std, self.league_std)
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))
