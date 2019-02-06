import os
import sys

import pytest

from aao.spiders.drivers import ChromeDriver


PROXY = os.environ['PROXY']


class TestChromeDriver:

    def test_set_headless_true(self):
        driver = ChromeDriver(headless=True)
        assert driver.options.headless

    @pytest.mark.skipif(
        sys.platform == 'linux', reason='not working in ci env')
    def test_set_headless_false(self):
        driver = ChromeDriver(headless=False)
        assert not driver.options.headless

    def test_set_window_size(self):
        driver = ChromeDriver(window_height=720, window_width=1280)
        assert driver.browser.get_window_size()['width'] <= 1280
        assert driver.browser.get_window_size()['height'] <= 720

    def test_set_user_agent(self):
        user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ('
                      'KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
        browser = ChromeDriver().browser
        agent_found = browser.execute_script("return navigator.userAgent")
        assert agent_found == user_agent

    def test_set_proxy(self):
        driver = ChromeDriver(proxy=PROXY)
        driver.browser.get('https://wtfismyip.com/text')
        ip_found = driver.browser.find_element_by_tag_name('body').text
        assert PROXY.split(':')[1][2:] == ip_found

    def test_set_proxy_not_a_str(self):
        with pytest.raises(TypeError, match='Proxy must be a string *'):
            ChromeDriver(proxy=['http', '1.1.1.1', '1'])

    def test_set_proxy_wrong_type(self):
        with pytest.raises(ValueError, match='Proxy supported type are *'):
            ChromeDriver(proxy='hello://1.1.1.1:1')

    def test_set_proxy_wrong_host(self):
        with pytest.raises(ValueError, match='Proxy host is not valid'):
            ChromeDriver(proxy='http://hello:1')

    def test_set_proxy_wrong_port(self):
        with pytest.raises(ValueError, match='Proxy port is not valid'):
            ChromeDriver(proxy='http://1.1.1.1:hello')

