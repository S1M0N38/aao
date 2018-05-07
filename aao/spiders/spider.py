import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


class Spider:
    def __init__(self, username=None, password=None, debug=False):
        self.logging(debug)
        self.username = username
        self.password = password
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--window-size=1920,1080")
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.implicitly_wait(8)
        self.wait = WebDriverWait(self.browser, 10)
        self.log.info('starting chrome browser')

    def homepage(self):
        self.log.debug(f'going to home page: {self.base_url}')
        self.browser.get(self.base_url)

    def logging(self, debug):
        self.log = logging.getLogger(self.name)
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        self.log.setLevel(logging.DEBUG)
        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        if debug:
            ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        # file handler
        log_file = f'log_{self.name}.log'
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        self.log.addHandler(fh)

    def quit(self):
        self.browser.quit()
        self.log.info(f'browser closed')
