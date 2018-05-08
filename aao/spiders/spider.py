from datetime import datetime
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


class Spider:
    def __init__(self, username=None, password=None, log_output=True,
                 log_save=True):
        self.logging(log_output, log_save)
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

    def logging(self, log_output, log_save):
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.DEBUG)
        # console handler
        if log_output:
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(message)s', '%H:%M:%S')
            ch.setFormatter(formatter)
            ch.setLevel(logging.INFO)
            self.log.addHandler(ch)
        # file handler
        if log_save:
            log_file = f'log_{self.name}.log'
            fh = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s-%(name)s-%(levelname)s-%(message)s')
            fh.setFormatter(formatter)
            self.log.addHandler(fh)

    def quit(self):
        self.browser.quit()
        self.log.info(f'browser closed')
