import unittest

from aao.spiders.spider_888sport import Spider888sport


@unittest.skip('not necessary')
class SpiderTest(unittest.TestCase):
    def setUp(self):
        self.s = Spider888sport(log_output=False)

    def tearDown(self):
        self.s.browser.quit()

    def test_soccer(self):
        pass


class SoccerTest(unittest.TestCase):
    def setUp(self):
        self.right_country_std = 'italy'
        self.right_league_std = 'serie_a'
        self.s = Spider888sport(log_output=False)

    def test_odds(self):
        events, odds = self.s.soccer.odds(
            self.right_country_std, self.right_league_std)
        self.assertGreater(len(events), 0)
        self.assertEqual(len(events), len(odds))

    def tearDown(self):
        self.s.browser.quit()
