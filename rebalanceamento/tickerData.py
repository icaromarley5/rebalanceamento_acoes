"""
Functions for collecting ticket data over the web
"""

import requests
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings("ignore")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'\
    ' AppleWebKit/537.36 (KHTML, like Gecko)'\
    ' Chrome/39.0.2171.95 Safari/537.36'}

def getAllTickers():
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
        pass
    return tickerList


def findTickerInfo(ticker):
    tickerInfo = None 

    try:
        tickerInfoAux = {'Ticker':ticker}

        url = 'https://www.fundamentus.com.br/detalhes.php?papel=' + ticker
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text)
        
        priceInfo = soup.find(
            'span',
            text='Cotação'
        ).find_next('td').text.replace(',','.')
        tickerInfoAux['Preço'] = float(priceInfo)
        vpaInfo = soup.find(
            'span',
            text='VPA'
        ).find_next('td').text.replace(',','.')
        tickerInfoAux['VPA'] = float(vpaInfo)
        pvpInfo = soup.find(
            'span',
            text='P/VP'
        ).find_next('td').text.replace(',','.')
        tickerInfoAux['PVP'] = float(pvpInfo)
        tickerInfoAux['Nome'] = soup.find(
            'span',
            text='Empresa'
        ).find_next('td').text.strip()
        
        tickerInfo = tickerInfoAux
    except Exception as e:
        pass

    return tickerInfo

def getAValidTickerCode():
    r = requests.get('https://www.fundamentus.com.br/detalhes.php',headers=headers)
    soup = BeautifulSoup(r.text)
    return soup.find('td').text.strip()