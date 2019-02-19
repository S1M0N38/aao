# Against all Odds

Aganist All Odds (aao) project aim to offert an eviroment where everyone 
can test his betting strategy on real odds. You can get the odds in two way: 
through **manual scraping** or using the **api**.

### Manual Scraping
aao provides a collection of spider that you can use to scrape some of the 
main betting sites. Sometime, due to country restrictions on these site, 
could be a bit tricky to set up a correct eviroment to scrape, 
but all the data are under your control. For more info read the Spider section.

### API
The api is easier to use; just sent the request using the methods that you 
find in the docs. The data that you get using the api method are provide 
by our website and sometimes could be down for maintenance.


## Installation
!> The pipenv (and pip) installation is not avaiable yet

I strongly recommend to use [pipenv](https://pipenv.readthedocs.io/en/latest/) 
to manage your virtual enviroment. With pipenv is really simple to group 
all the enviroment variables in a single file (the *.env*).

### For simple usage
In order to install aao, open your terminal, go to your project directory and 
type
```bash
pipenv install aao
```
It's really import to have the last version to ensure the correct functioning 
of the library; so sometimes do
```bash
pipenv update aao
```
If you plan to use the **manual scraping** you need also to install 
[chromedrivers](http://chromedriver.chromium.org/) (and of course you have to 
have chorome or chromiunm installed). If have ubuntu take a took at the 
[Makefile](https://github.com/S1M0N38/aao/blob/master/Makefile) and try 
the commands under *chromedriver* section. 
For all other os google how to install chromedriver.


### For more advance use and dev purpose
For install the whole aao packege (with also test depencencies) use
```bash
pipenv install aao --dev
```

After doing that you need to setup enviroment variables used by the test suit.
If you use pipenv you have to add *.env* at the root of your project with the 
following variables

```.env
PROXY="http://123.123.123:123"

# BET365
USERNAME_BET365="username_bet365"
PASSWORD_BET365="password_bet365"

# 888SPORT
PROXY_BET365="http://123.123.123:123"

...
{VALUE}_{BOOKMAKER}="value"
```

With the *.env* file you can specify `**kargs` passed to the spider. 
