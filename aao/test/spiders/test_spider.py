import os

import pytest

from aao.spiders import spiders


class TestSpider:

    @pytest.fixture(scope='class', params=spiders.values())
    def spider(self, request):
        s = request.param()
        yield s
        s.quit()

    odds = ['+400', '-260', '2/11', '3.54']
    @pytest.mark.parametrize('odd', odds)
    def test_odd2decimal(self, spider, odd):
        result = spider.odd2decimal(odd)
        assert isinstance(result, float)

    def test_quit(self, spider):
        spider.quit()
        assert getattr(spider.browser.service.process, 'pid', None) is None

