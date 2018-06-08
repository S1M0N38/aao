import json
import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.support.ui import WebDriverWait


class Spider:
    def __init__(self, username=None, password=None, log_level_console='INFO',
                 log_level_file='DEBUG', browser='CHROME', explicit_wait=5,
                 implicitly_wait=5, headless=False, proxy=None):

        self.config = {
            'log_level_console': log_level_console,
            'log_level_file': log_level_file,
            'log_file': f'log_{self.name}.log',
            'browser': browser,
            'explicit_wait': explicit_wait,
            'implicitly_wait': implicitly_wait,
            'headless': headless,
            'proxy': proxy,
        }

        self.log = self.get_logger()
        self.table = self.get_table()
        self.browser = self.get_browser()
        self.wait = WebDriverWait(self.browser, explicit_wait)
        self.username = username
        self.password = password
        self.log_config()
        self.log.info('starting browser...')

    def get_logger(self):
        log = logging.getLogger(self.name)
        log.setLevel(logging.DEBUG)
        # console handler
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(message)s', '%H:%M:%S')
        ch.setFormatter(formatter)
        ch.setLevel(self.config['log_level_console'])
        log.addHandler(ch)
        # file handler
        fh = logging.FileHandler(self.config['log_file'])
        formatter = logging.Formatter(
            '%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(self.config['log_level_file'])
        log.addHandler(fh)
        return log

    def get_browser(self):
        if self.config['browser'] == 'CHROME':
            user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
            options = chrome_options()
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            if self.config['proxy'] is not None:
                proxy = self.config["proxy"]
                options.add_argument(f'--proxy-server={proxy}')
            if self.config['headless']:
                options.add_argument('--headless')
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument('--lang=en')
            browser = webdriver.Chrome(options=options)
            browser.implicitly_wait(self.config['implicitly_wait'])
            return browser
        # add other browser
        else:
            raise KeyError(
                'browser name error: choose form "CHROME"')

    def get_table(self):
        file_path = os.path.dirname(__file__)
        table_path = os.path.join(file_path, 'tables', f'{self.name}.json')
        with open(table_path) as f:
            table = json.load(f)
        return table

    def log_config(self):
        self.log.debug(' < SPIDER CONFIGURATION > ')
        self.log.debug(
            f' + browser -> {self.config["browser"]}')
        self.log.debug(
            f' + log_level_console -> {self.config["log_level_console"]}')
        self.log.debug(
            f' + log_level_file -> {self.config["log_level_file"]}')
        self.log.debug(
            f' + explicit_wait -> {self.config["explicit_wait"]} sec')
        self.log.debug(
            f' + implicitly_wait -> {self.config["implicitly_wait"]} sec')
        self.log.debug(
            f' + headless -> {self.config["headless"]}')

    def homepage(self):
        self.log.debug(f'opening to homepage: {self.base_url}')
        self.browser.get(self.base_url)

    def quit(self):
        self.browser.quit()
        self.log.info(f'browser closed')
