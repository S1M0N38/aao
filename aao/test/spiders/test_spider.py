import pytest

from aao.spiders import spiders


class TestSpider:

    @pytest.mark.parametrize('spider', spiders)
    def test_quit(self, spider):
        s = spider()
        s.quit()
        assert getattr(s.browser.service.process, 'pid', None) is None

