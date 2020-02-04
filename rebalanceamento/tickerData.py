"""
Functions for collecting ticket data over the web
"""

from django.conf import settings

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup
import re

import threading

import time

browser = None
urlCEI = 'https://cei.b3.com.br/CEI_Responsivo/login.aspx?MSG=SOUT'
def createBrowser(visible=False):
    path = settings.BASE_DIR + '\\rebalanceamento\\chromedriver'
    chromeOptions = Options()
    if not visible:
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--window-size=1366x1280")
        chromeOptions.add_argument('log-level=2')
    return WebDriver(path, chrome_options=chromeOptions)        

def loadBrowser():
    global browser
    if not browser:
        browser = createBrowser()
        browser.get(urlCEI)

threadCreateBrowser = threading.Thread(
    target=loadBrowser,
    daemon=True)
threadCreateBrowser.start()

def destroyBrowser():
    global browser
    while threading.main_thread().is_alive():
        time.sleep(5)
    browser.quit()
threadDestroyBrowser = threading.Thread(target=destroyBrowser)
threadDestroyBrowser.start()
       
waitTime = 120
  
tickerInputBuffer = {
}
tickerOutputBuffer = {
}   
def getTickerInfo():
    while True:
        keys = list(tickerInputBuffer.keys())
        if keys:
            cpf = keys[0]
            password = tickerInputBuffer.pop(cpf)
            try:
                data = _getCEIdata(cpf,password)
                data['Preço'] = _getTickersPrice(data['Ticker'])
                tickerOutputBuffer[cpf] = data
            except Exception as e:
                tickerOutputBuffer[cpf] = 'Fail'
threading.Thread(target=getTickerInfo, daemon=True).start()

def _getCEIdata(cpf, password):
    try:
        WebDriverWait(browser, waitTime).until(
            lambda browser: browser.current_url== urlCEI)
        data = {
            'Ticker': [],
            'Quantidade': [],
        }    
        inputElement = browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_txtLogin")
        inputElement.send_keys(cpf)
        inputElement = browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_txtSenha")
        inputElement.send_keys(password)
        inputElement.send_keys(Keys.RETURN)
            
        WebDriverWait(browser, waitTime).until(
            lambda browser: browser.current_url
                == 'https://cei.b3.com.br/CEI_Responsivo/home.aspx')           
        
        url = 'https://cei.b3.com.br/CEI_Responsivo/'\
            'ConsultarMovimentoCustodia.aspx?TP_VISUALIZACAO=1'
        browser.get(url)
        
        tbody = browser.find_element_by_tag_name('table')\
            .find_element_by_tag_name('tbody')
        
        for tr in tbody.find_elements_by_tag_name('tr'):
            tdList = tr.find_elements_by_tag_name('td')
            data['Ticker'].append(tdList[2].text.strip())
            data['Quantidade'].append(
                int(tdList[5].text.strip()))
    except Exception as e:
        raise Exception('Data not found')
    finally:
        browser.get(urlCEI)
    return data

def _getTickersPrice(tickerList):     
    resultDict = {ticker: 0 for ticker in tickerList}
    
    threadList = []
    for ticker in tickerList:
        thread = threading.Thread(
            target=_getTickerPrice,
            args=[ticker, resultDict])
        thread.start()
        threadList.append(thread)
    
    [thread.join() for thread in threadList]
    
    if any(map(lambda x: x == 0, resultDict.values())):
        raise Exception('Data not found')
    return list(resultDict.values())

def _processTicker(ticker):
    ticker = ticker[:-1] if ticker[-1] == 'F' else ticker
    return ticker.lower()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'\
    ' AppleWebKit/537.36 (KHTML, like Gecko)'\
    ' Chrome/39.0.2171.95 Safari/537.36'
}
regex = re.compile('.+Venda = .+')
def _getTickerPrice(ticker, tickerDict):
    try:
        url = 'http://www.grafbolsa.net/cgi-bin/al.pl/' + _processTicker(ticker)
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text)
        tickerDict[ticker] = \
            float(soup.find(
                text= regex).split('Venda = ')[1].strip())
    except:
        pass