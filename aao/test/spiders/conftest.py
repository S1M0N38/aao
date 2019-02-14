import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--proxy',
        help='proxy for driver e.g. http://123.12.123.11:40)')
    parser.addoption(
        '--notheadless', action='store_false',
        help='run the driver not in headless mode')


@pytest.fixture(scope='session')
def confspider(request):
    return dict(
        proxy=request.config.getoption('--proxy'),
        headless=request.config.getoption('--notheadless'),
    )



