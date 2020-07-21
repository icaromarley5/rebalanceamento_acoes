"""
Functions for collecting ticket data over the web
"""

import requests
from bs4 import BeautifulSoup

from django.core.cache import cache

import logging

import warnings
warnings.filterwarnings("ignore")

def searchCache(f, id_cache, timeout):
    return cache.get_or_set(id_cache, f, timeout)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'\
    ' AppleWebKit/537.36 (KHTML, like Gecko)'\
    ' Chrome/39.0.2171.95 Safari/537.36'}

def _getTickerListF():
        tickerList = []
        try:
            url = 'https://www.fundamentus.com.br/detalhes.php'
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text)

            tbody = soup.find('tbody')
            tickerList = [
                a.text.strip() for a in tbody.findAll('a')
            ]
        except Exception as e:
            logging.error(e)
        return tickerList

def getTickerList():
    timeout = 60 * 60 * 24 * 2 # 2 day
    id_cache = 'tickerList'
    return searchCache(_getTickerListF, id_cache, timeout)

def _getTickerInfoF(ticker):
    tickerInfo = None
    try:
        tickerInfoAux = {'ticker':ticker}

        url = 'https://www.fundamentus.com.br/detalhes.php?papel=' + ticker
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text)

        priceInfo = soup.find(
            'span',
            text='Cotação'
        ).find_next('td').text.replace(',','.')

        if float(priceInfo) == 0:
            raise Exception('Data incomplete')

        vpaInfo = soup.find(
            'span',
            text='VPA'
        ).find_next('td').text.replace(',','.')
        tickerInfoAux['vpa'] = float(vpaInfo)

        pvpInfo = soup.find(
            'span',
            text='P/VP'
        ).find_next('td').text.replace(',','.')
        tickerInfoAux['pvp'] = float(pvpInfo)

        tickerInfo = tickerInfoAux
    except Exception as e:
        pass
    return tickerInfo

def _getTickerPriceF(ticker):
    price = None
    try:
        url = f'https://statusinvest.com.br/acoes/{ticker.lower()}'
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text)

        price = soup.find(
            'div',
            title='Valor atual do ativo'
        ).find_next('strong').text.replace(',','.')
        price = float(price)

    except Exception as e:
        pass
    return price

def getTickerInfo(ticker):
    timeout = 60 * 60 * 24 * 7 # 1w
    id_cache = ticker + 'info'

    info = searchCache(
        lambda : _getTickerInfoF(ticker),
         id_cache,
         timeout
    )

    if info:
        timeout = 60 * 20 # 20 min
        id_cache = ticker + 'price'

        price = searchCache(
            lambda : _getTickerPriceF(ticker),
            id_cache,
            timeout
        )
        if price:
            info['price'] = price
        else:
            info = None
    return info

def getAValidTickerCode(i=0):
    r = requests.get(
        'https://www.fundamentus.com.br/detalhes.php',
        headers=headers,
    )
    soup = BeautifulSoup(r.text)

    tbody = soup.find('tbody')
    tr = tbody.findAll('tr')[i]
    return tr.find('td').text.strip()
