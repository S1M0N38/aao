# Spiders

Now this project support 4 bookmakers: bet365, 888sport, Bwin and William Hill. To scrape with againstallodds, first define a spider in one of the following way. The *SpiderBet365* only scrape *bet365*, *Spider888sport* only *888sport*, and so on ...
Every country have differnt about gambling, so we decide to develope the spiders to work on the english version of the sites but isn't so easy to access that version in you came from another country. Every bookmaker have a differnt configuration

----

## Define a Spider

### Bet365
```python
from aao.spiders import SpiderBet365

spider = SpiderBet365(username='username', password='password')
```
If you try to use a VPN with bet365 the site doesn't work.
So, if you want to access to the english version you have to create
a *english account*. Creating an account is free and you do not even
have to verify your identity.

### 888sport
```python
from aao.spiders import Spider888sport

spider = Spider888sport()
```
No account needed, working with a German proxy

### Bwin
```python
from aao.spiders import SpiderBwin

spider = SpiderBwin()
```
No account needed, working with a German proxy

### William Hill
```python
from aao.spiders import SpiderWilliamhill

spider = SpiderWilliamhill()
```
No account needed, working with a German proxy

----

## Scrape with a Spider
After you have define a spider, now you are ready to scrape odds for any sports.

### Soccer

> For Great Britain, soccer means football.

We decice to name it 'Soccer' in order to avoid confusion
with 'American football'.
```python
events, odds = spider.soccer.odds('italy', 'serie_a')
```
**.soccer.odds()** function accepts to arguments: **country** and **leagues**.
Bookmakers support different leagues but major leagues are avaiable on every
bookmaker. Take a look at the *sports/soccer* for a list of supported leagues.

### OtherSport
!> soccer is the only supported sport
```python
odds = spider.other_sport.odds('foo', 'foo')
```
