# Spiders

Now this project support 4 bookmakers: bet365, 888sport, Bwin and William Hill. To scrape with againstallodds, first define a spider in one of the following way. The *SpiderBet365* only scrape *bet365*, *Spider888sport* only *888sport*, and so on ...
Every country have differnt about gambling, so we decide to develope the spiders to work on the english version of the sites but isn't so easy to access that version in you came from another country. Every bookmaker have a differnt configuration

----

## Define a Spider

### Bet365
```python
from aao.scraper.spider_bet365 import SpiderBet365

spider = SpiderBet365('username', 'password')
```
If you try to use a VPN with bet365 the site doesn't work. So, if you want to access to the english version you have to create a *english account*. Creating an account is free and you do not even have to verify your identity.

### 888sport
```python
from aao.spiders.spider_888sport import Spider888sport

spider = Spider888sport()
```
No account needed, working with a German VPN

### Bwin
```python
from aao.spiders.spider_bwin import SpiderBwin

spider = SpiderBwin()
```
No account needed, working with a German VPN

### William Hill
```python
from aao.spiders.spider_williamhill import SpiderWilliamhill

spider = SpiderWilliamhill()
```
No account needed, working with a German VPN

----

## Scrape with a Spider

After you have define a spider, now you are ready to scrape odds for any sports.

### Soccer
> For Great Britain, soccer means football. We decice to name it 'Soccer' in order to avoid confusion with 'American football'

```python
odds = spider.soccer.odds('italy', 'serie_a')
```

*.soccer.odds()* function accepts to arguments: **country** and **leagues**. Bookmakers support different leagues but major leagues are avaiable on every bookmaker. Down here there is the list of supported leagues

### OtherSport

```python
odds = spider.other_sport.odds('foo', 'foo')
```

add. other sports here ...
