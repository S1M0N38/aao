from abc import ABC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait


class Driver(ABC):

    def __init__(self, headless=True, explicit_wait=5, implicit_wait=5,
                 proxy=None, window_height=1080, window_width=1920, **kwargs):

        self.headless = headless
        self.explicit_wait = explicit_wait
        self.implicit_wait = implicit_wait
        self.proxy = proxy
        self.window_size = (window_height, window_width)


class ChromeDriver(Driver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = ChromeOptions()
        self._set_headless()
        self._set_window_size()
        self._set_user_agent()
        self._set_proxy()
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.implicitly_wait(self.implicit_wait)
        self.wait = WebDriverWait(self.browser, self.explicit_wait)

    def _set_headless(self):
        if self.headless:
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-dev-shm-usage')
            self.options.add_argument('--no-sandbox')

    def _set_window_size(self):
        size = f'{self.window_size[1]},{self.window_size[0]}'
        self.options.add_argument(f'--window-size={size}')

    def _set_user_agent(self):
        user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ('
                      'KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
        self.options.add_argument(f'user-agent={user_agent}')
        self.options.add_argument('--lang=en')

    def _set_proxy(self):
        if self.proxy is None:
            return
        if not isinstance(self.proxy, str):
            raise TypeError('Proxy must be a string, e.g. "http://1.1.1.1:1"')
        type_, host, port, *auth = self.proxy.split(':')
        types = ('http', 'https', 'socks5')
        if type_ not in types:
            raise ValueError(f'Proxy supported type are {types}')
        if not host[2:].replace('.', '').isdigit():
            raise ValueError('Proxy host is not valid')
        if not port.isdigit():
            raise ValueError('Proxy port is not valid')
        self.options.add_argument(f'--proxy-server={self.proxy}')

