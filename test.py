import argparse
import importlib
import subprocess
import sys
import time
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
        tests = loader.loadTestsFromTestCase(test)
        suite.addTest(tests)
    runner = unittest.TextTestRunner(
        verbosity=args.verbose, failfast=args.failfast)
    try:
        runner.run(suite)
    finally:
        vpn.kill()


def setup_vpn():
    if sys.platform in ['linux', 'linux2', 'darwin']:
        old_ip = subprocess.run(
            ['curl', '-s', 'ipinfo.io/ip'], stdout=subprocess.PIPE).stdout
        url = ('https://gist.githubusercontent.com/S1M0N38/bb6403808c7532d96b6'
               'ad6e5d79b6abd/raw/a9d9889ffb3dd84983bad3a4a931581981b47b51/vpn.py')
        subprocess.run(['curl', '-s', url, '-o', 'vpn.py'])
        global vpn
        vpn = subprocess.Popen(['sudo', 'python', 'vpn.py' ])
        time.sleep(10)
        new_ip = subprocess.run(
            ['curl', '-s', 'ipinfo.io/ip'], stdout=subprocess.PIPE).stdout
        if old_ip != new_ip:
            print(f'{old_ip.decode("utf-8")[:-1]} -> {new_ip.decode("utf-8")}')
        else:
            raise KeyError('something went wrong with vpn setup :(')
    else:
        raise KeyError('Your os is not compatible with --vpn argument')


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
        '-vpn', action='store_true',
        help='setup vpn for avoinding country ban')
    args = parser.parse_args()
    if args.vpn:
        setup_vpn()
    test_run(args)


if __name__ == '__main__':
    main()


'''
---- Install OpenVPN Linux (Ubuntu) ----
- sudo apt-get install openvpn

------- Install OpenVPN Mac OS ---------
- install brew
- brew install openvpn
- Add this to your ~/.bash_profile or wherever you save ENV variable
  PATH=$(brew --prefix openvpn)/sbin:$PATH

------- Install OpenVPN Windows --------
- install a gui tool but you can't use this -vpn argument
'''
