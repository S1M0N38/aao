import unittest

from aao.spiders.spider_williamhill import SpiderWilliamhill


class SpiderTest(unittest.TestCase):
    headless = False
    log_level = 'CRITICAL'

    @classmethod
    def setUpClass(self):
        self.s = SpiderWilliamhill(log_level_console=self.log_level,
                                   headless=self.headless)

    @classmethod
    def tearDownClass(self):
        self.s.quit()

    def test_change_odds_format(self):
        self.s.change_odds_format('AMERICAN')
        xpath = '//option[text()="American" and @selected="true"]'
        option = self.s.browser.find_elements_by_id('oddsDisplay')
        self.assertTrue(option)

    def test_soccer(self):
        self.s.soccer
        h2_elements = self.s.browser.find_elements_by_tag_name('h2')
        h2_text = [h2.text for h2 in h2_elements]
        self.assertIn('All Competitions', h2_text)


class SoccerTest(unittest.TestCase):
    headless = False
    log_level = 'CRITICAL'

    @classmethod
    def setUpClass(self):
        self.s = SpiderWilliamhill(log_level_console=self.log_level,
                                   headless=self.headless)
        # country
        self.country_not_exists = 'this_country_does_not_exixts'
        self.country_null = 'test_country_null'
        self.country_foo = 'test_country_foo'
        self.country_std = 'world_cup_2018'
        self.country = 'World Cup 2018'
        # league
        self.league_not_exists = 'this_league_does_not_exixts'
        self.league_null = 'test_league_null'
        self.league_foo = 'test_league_foo'
        self.league_std = 'group_a'
        self.league = 'World Cup 2018 - Group A'

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
        msg = (f'{self.country_foo} - {self.league_foo} not found on '
               f'{self.s.name} site')
        self.assertIn(msg, str(context.exception))

    def test_odds_right(self):
        events, odds = self.s.soccer.odds(self.country_std, self.league_std)
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))
