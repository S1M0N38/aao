import unittest

from aao.spiders.spider_bwin import SpiderBwin


@unittest.skip('not necessary')
class SpiderTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.s = SpiderBwin(log_level_console='CRITICAL')

    @classmethod
    def tearDownClass(self):
        self.s.quit()

    def test_soccer(self):
        pass


class SoccerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.right_sport = ''
        self.wrong_country = 'this_country_does_not_exixts'
        self.right_country_std = 'italy'
        self.wrong_league = 'this_league_does_not_exixts'
        self.right_league_std = 'serie_a'
        self.not_supported_league_std = 'primavera_2_group_a'
        self.s = SpiderBwin(log_level_console='CRITICAL')

    @classmethod
    def tearDownClass(self):
        self.s.quit()

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
