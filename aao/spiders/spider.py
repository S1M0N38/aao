import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from .logger import logger


class Spider:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--window-size=1920,1080")
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.implicitly_wait(8)
        self.wait = WebDriverWait(self.browser, 10)

        self.logging()

    def homepage(self):
        self.logger.info(f'requesting {self.base_url}')
        self.browser.get(self.base_url)

    def logging(self):
        log_file = 'log_{}.log'.format(self.name)
        fh = logging.FileHandler(log_file)
        form = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        fh.setFormatter(form)
        self.logger = logger
        self.logger.addHandler(fh)

    def quit(self):
        self.browser.quit()
        self.logger.info(f'{self.name} closed')
