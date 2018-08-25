import argparse
import importlib
import sys
import unittest


def test_run(args):
    test_file = f'aao.test.test_{args.spider}'
    test_module = importlib.import_module(test_file)
    test_name = [n for n in dir(test_module) if n.endswith('Test')]
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in test_name:
        test = getattr(test_module, name)
        test.headless = args.headless
        test.log_level = args.log
        test.proxy = args.proxy
        tests = loader.loadTestsFromTestCase(test)
        suite.addTest(tests)
    runner = unittest.TextTestRunner(
        verbosity=args.verbose, failfast=args.failfast)
    test_runner = runner.run(suite)
    ret = not test_runner.wasSuccessful()
    sys.exit(ret)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'spider', type=str,
        choices=['bet365', 'bwin', '888sport', 'williamhill'],
        help='choose the spider')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='increase output verbosity')
    parser.add_argument(
        '-f', '--failfast', action='store_true',
        help='stop on first fail or error')
    parser.add_argument(
        '-hd', '--headless', action='store_true',
        help='run spider in headless mode')
    parser.add_argument(
        '-log', default='CRITICAL',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='set console log level')
    parser.add_argument(
        '-p', '--proxy', type=str, default=None,
        help=('use proxy in selenium for avoinding country ban. '
              'e.g https://123.123.13:71 [type]://[host]:[port]'
              'Use "auto" for search for free proxy (not reliable)'))
    args = parser.parse_args()
    test_run(args)


if __name__ == '__main__':
    main()
