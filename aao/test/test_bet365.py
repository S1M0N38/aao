import os
import unittest

from aao.spiders.spider_bet365 import SpiderBet365

username = os.environ.get('USER_BET365')
password = os.environ.get('PASS_BET365')


class SpiderTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.s = SpiderBet365(username, password, log_output=False)

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
    @classmethod
    def setUpClass(self):
        self.right_sport = 'Soccer'
        self.wrong_country = 'this_country_does_not_exixts'
        self.right_country = 'Italy'
        self.right_country_std = 'italy'
        self.wrong_league = 'this_league_does_not_exixts'
        self.right_league = 'Italy Serie A'
        self.right_league_std = 'serie_a'
        self.not_supported_league_std = 'primavera_2_group_a'
        self.s = SpiderBet365(username, password, log_output=False)

    @classmethod
    def tearDownClass(self):
        self.s.quit()

    def setUp(self):
        self.s.homepage()

    def test_country_wrong_name(self):
        with self.assertRaises(KeyError) as context:
            self.s.soccer._country(self.wrong_country)
        self.assertIn(self.wrong_country, str(context.exception))

    def test_country_right(self):
        self.s.soccer._country(self.right_country)
        self.assertEqual(self.right_country, self.s.soccer.country)

    def test_league_wrong_name(self):
        self.s.soccer._country(self.right_country)
        with self.assertRaises(KeyError) as context:
            self.s.soccer._league(self.wrong_league)
        self.assertIn(self.wrong_league, str(context.exception))

    def test_league_right(self):
        self.s.soccer._country(self.right_country)
        self.s.soccer._league(self.right_league)
        xpath = '//div[@class="cl-BreadcrumbTrail "]'
        breadcrumb = self.s.browser.find_element_by_xpath(xpath)
        sport_found, _, league_found = breadcrumb.text.split('\n')
        self.assertEqual(self.right_sport, sport_found)
        self.assertEqual(self.right_league, league_found)

    def test_matches_wrong_country_and_league(self):
        with self.assertRaises(KeyError) as context:
            self.s.soccer._matches(self.wrong_country, self.right_league)
        self.assertIn(self.wrong_country, str(context.exception))
        with self.assertRaises(KeyError) as context:
            self.s.soccer._matches(self.right_country, self.wrong_league)
        self.assertIn(self.wrong_league, str(context.exception))

    def test_matches_right(self):
        events, odds = self.s.soccer._matches(
            self.right_country, self.right_league)
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))

    def test_odds_wrong(self):
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.wrong_country, self.right_league_std)
        self.assertIn(self.wrong_country, str(context.exception))
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.right_country_std, self.wrong_league)
        self.assertIn(self.wrong_league, str(context.exception))
        with self.assertRaises(KeyError) as context:
            self.s.soccer.odds(self.right_country_std,
                               self.not_supported_league_std)
        self.assertIn(self.not_supported_league_std, str(context.exception))

    def test_odds_right(self):
        events, odds = self.s.soccer.odds(
            self.right_country_std, self.right_league_std)
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))
