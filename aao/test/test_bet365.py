import os
import unittest

from aao.spiders.spider_bet365 import SpiderBet365


class SpiderTest(unittest.TestCase):
    headless = False
    log_level = 'CRITICAL'
    proxy = None
    username = os.environ.get('USER_BET365')
    password = os.environ.get('PASS_BET365')

    @classmethod
    def setUpClass(self):
        self.s = SpiderBet365(self.username, self.password,
                              log_level_console=self.log_level,
                              headless=self.headless,
                              proxy=self.proxy)

    @classmethod
    def tearDownClass(self):
        self.s.quit()

    def setUp(self):
        self.s.homepage()

    def test_change_odds_format(self):
        self.s.change_odds_format('American')
        xpath = ('//a[@class="hm-DropDownSelections_Item hm-DropDown'
                 'Selections_ItemHighlight "][text()="American"]')
        format_select = self.s.browser.find_elements_by_xpath(xpath)
        self.assertTrue(format_select)
        self.s.change_odds_format('Decimal')

    def test_soccer(self):
        self.s.soccer
        xpath = ('//div[@class="wn-Classification wn-Classification_Selected'
                 ' "][text() = "Soccer"]')
        is_soccer_open = self.s.browser.find_elements_by_xpath(xpath)
        self.assertTrue(is_soccer_open)


class SoccerTest(unittest.TestCase):
    headless = False
    log_level = 'CRITICAL'
    proxy = None
    username = os.environ.get('USER_BET365')
    password = os.environ.get('PASS_BET365')

    @classmethod
    def setUpClass(self):
        self.s = SpiderBet365(self.username, self.password,
                              log_level_console=self.log_level,
                              headless=self.headless,
                              proxy=self.proxy)
        # country
        self.country_not_exists = 'this_country_does_not_exixts'
        self.country_null = 'test_country_null'
        self.country_foo = 'test_country_foo'
        self.country_std = 'england'
        self.country = 'United Kingdom'
        # league
        self.league_not_exists = 'this_league_does_not_exixts'
        self.league_null = 'test_league_null'
        self.league_foo = 'test_league_foo'
        self.league_std = 'premier_league'
        self.league = 'England Premier League'

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

    def test_country_and_league_not_found(self):
        msg_ = 'it seams that not odds are avaiable for this'
        # when there aren't avaible odds in a country, it isn't shown anymore
        # but in spider table it appeare as supported and avaiable
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.country_foo, self.league_foo)
        msg = (f'{self.country_foo} not found on {self.s.name} site, {msg_}')
        self.assertIn(msg, str(context.exception))
        # it's the same with league. Here it used the open session to force
        # _league() with out calling s.soccer.odds()
        with self.assertRaises(KeyError) as context:
            self.s.soccer._league()
        msg = (f'{self.league_foo} not found on {self.s.name} site, {msg_}')
        self.assertIn(msg, str(context.exception))

    def test_odds_right(self):
        events, odds = self.s.soccer.odds(self.country_std, self.league_std)
        path = self.s.browser.find_element_by_class_name('cl-BreadcrumbTrail')
        league = self.s.table['soccer']['leagues'][self.country_std][self.league_std]
        self.assertIn(league, path.text)  # check if the league is correct
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))
