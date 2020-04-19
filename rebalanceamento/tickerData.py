"""
Functions for collecting ticket data over the web
"""

from django.conf import settings

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

import threading

def processCSV(csvFile):
    df = pd.DataFrame([])
    try:
        data = pd.read_csv(csvFile,sep='\t')
        expected_columns = [
            'Empresa', 'Tipo', 'Cód. de Negociação', 
            'Cod.ISIN', 'Preço (R$)*','Qtde.', 
            'Fator Cotação', 'Valor (R$)']
        
        tickerRegex = '^[\dA-Z]{4}([345678]|11|12|13)$'
        if all(data.columns == expected_columns) \
            and data['Qtde.'].dtype == np.dtype('int64') \
            and all(data['Cód. de Negociação'].str.contains(tickerRegex, regex=True)):
                data = data[['Cód. de Negociação','Qtde.']]
                data.columns = ['Ticker','Quantidade']
                data['Quantidade'] = data['Quantidade'].astype(int) 
                df = data
        else:
            raise Exception('Unexpected data')
    except Exception as e:
        pass
    return df

def addTickerInfo(data):
    try:
        resultDict = {ticker: {'Preço':None, 'VPA':None} for ticker in data['Ticker']}

        threadList = []
        for ticker in data['Ticker']:
            thread = threading.Thread(
                target=_getTickerInfo,
                args=[ticker, resultDict])
            thread.start()
            threadList.append(thread)
        
        [thread.join() for thread in threadList]
    
        priceList = []
        VPAList = []
        for ticker, info in resultDict.items():
            priceList.append(info['Preço'])
            VPAList.append(info['VPA'])

        if not resultDict or None in priceList + VPAList:
            raise Exception('Data not found')
    
        data['Preço'] = priceList
        data['VPA'] = VPAList
    except Exception as e:
        raise e
    return data

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'\
    ' AppleWebKit/537.36 (KHTML, like Gecko)'\
    ' Chrome/39.0.2171.95 Safari/537.36'}
def _getTickerInfo(ticker, tickerDict):
    try:
        url = 'https://www.fundamentus.com.br/detalhes.php?papel=' + ticker
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text)
        
        tickerDict[ticker]['Preço'] = \
            float(soup.find(
                'span',
                text='Cotação').find_next('td').text.replace(',','.'))
        tickerDict[ticker]['VPA'] = \
            float(soup.find(
                'span',
                text='VPA').find_next('td').text.replace(',','.'))
    except Exception as e:
        pass