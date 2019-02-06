import os

import pytest

from aao.spiders import spiders


class TestSpider:

    @pytest.mark.parametrize('spider', spiders)
    def test_quit(self, spider):
        if spider.bookmaker == 'bet365':
            username = os.environ['BET365_USERNAME']
            password = os.environ['BET365_PASSWORD']
            s = spider(username=username, password=password)
        else:
            s = spider()
        s.quit()
        assert getattr(s.browser.service.process, 'pid', None) is None

