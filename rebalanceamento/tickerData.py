"""
Functions for collecting ticket data over the web.
"""

import requests
from bs4 import BeautifulSoup
import json

from django.core.cache import cache

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
        url = ('https://statusinvest.com.br/category/advancedsearchresult'
            '?search=%7B%22Sector%22%3A%22%22%2C%22SubSector%22%3A%22%22%2'
            'C%22Segment%22%3A%22%22%2C%22my_range%22%3A%220%3B25%22%2C%22'
            'dy%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_L'
            '%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_VP%2'
            '2%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_Ativo%'
            '22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemBr'
            'uta%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22marg'
            'emEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22ma'
            'rgemLiquida%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%'
            '22p_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22e'
            'V_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22divi'
            'daLiquidaEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%'
            '22dividaliquidaPatrimonioLiquido%22%3A%7B%22Item1%22%3Anull%2C%22Item'
            '2%22%3Anull%7D%2C%22p_SR%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3'
            'Anull%7D%2C%22p_CapitalGiro%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22'
            '%3Anull%7D%2C%22p_AtivoCirculante%22%3A%7B%22Item1%22%3Anull%2C%22It'
            'em2%22%3Anull%7D%2C%22roe%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3A'
            'null%7D%2C%22roic%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C'
            '%22roa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezC'
            'orrente%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22pl_Ativo%'
            '22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22passivo_Ativo%22%3'
            'A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22giroAtivos%22%3A%7B%22I'
            'tem1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22receitas_Cagr5%22%3A%7B%22Item1'
            '%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lucros_Cagr5%22%3A%7B%22Item1%22%3'
            'Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezMediaDiaria%22%3A%7B%22Item1%22'
            '%3Anull%2C%22Item2%22%3Anull%7D%7D&CategoryType=1'
        )
        r = requests.get(url, headers=headers)

        result = json.loads(r.text)
        tickerList = [
            company['ticker'] for company in result
        ]
    except Exception as e:
        pass
    return tickerList

def getTickerList():
    timeout = 60 * 60 * 24 * 14 # 14 days
    id_cache = 'tickerList'
    return searchCache(_getTickerListF, id_cache, timeout)

def _getTickerInfoF(ticker):
    tickerInfo = None
    try:
        tickerInfoAux = {'ticker':ticker}

        url = f'https://statusinvest.com.br/acoes/{ticker.lower()}'
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text)

        vpaInfo = soup.find(
            'h3',
            text='VPA'
        ).find_next('strong').text.replace(',','.')
        tickerInfoAux['vpa'] = float(vpaInfo)

        pvpInfo = soup.find(
            'h3',
            text='P/VP'
        ).find_next('strong').text.replace(',','.')
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
        timeout = 60 * 60 # 1 h
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
        'https://statusinvest.com.br/',
        headers=headers,
    )
    soup = BeautifulSoup(r.text)

    ticker = soup.find('h4',
        {'title':'ticker/código do ativo'}).text.split()[0].strip()
    return ticker
