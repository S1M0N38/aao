from abc import ABC

from .drivers import ChromeDriver
from .logger import logger
from .tables import table


class Spider(ABC):
    """Abstract Base Class for every spider

    User must not init this class, but only the particular Spider class
    (e.g. SpiderBet365(...)). Every spider inherit from this class.

    Attributes
        driver (:obj:`Driver`): The driver obj, contains browser and wait.
        browser (:obj:`webdriver`): Selenium browser using for web-scrape.
        wait (:obj:`WebDriverWait`): It waits for the page loading.
        table (:obj:`list`): contains data about all competitions.

    """

    def __init__(self, driver=ChromeDriver,
                 username=None, password=None, **kwargs):
        """Init the spider, open the browser and start the log

        Args:
            driver (:obj:`Driver`): The driver obj, contains browser and wait.
            **kwargs: Keyword arguments passed to the `driver` and to `log`.

        """
        self.driver = driver(**kwargs)
        self.browser = self.driver.browser
        self.wait = self.driver.wait
        self.log = logger(self.bookmaker, **kwargs)
        self.table = table(self.bookmaker)
        self.log.info('starting spider…')

    @staticmethod
    def odd2decimal(odd: str):
        if '+' in odd:
            return round(int(odd[1:]) / 100 + 1, 2)
        elif '-' in odd:
            return round(100 / int(odd[1:]) + 1, 2)
        elif '/' in odd:
            numerator, denominator = odd.split('/')
            return round(int(numerator) / int(denominator) + 1, 2)
        elif '.' in odd or ',' in odd:
            return round(float(odd), 2)
        else:
            return None

    def quit(self):
        """Close the broswer session in a clean manner."""
        self.browser.quit()
        self.log.info(f'spider closed')

