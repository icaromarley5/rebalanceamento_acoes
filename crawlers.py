# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 22:38:21 2020

@author: icaromarley5
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import re

def get_browser():
    return webdriver.PhantomJS()
    
def get_cei_data(cpf,password):
    data = {
        'Ticker':[],
        'Quantidade':[],
    }
    
    browser = get_browser()
   
    try:
        url = 'https://cei.b3.com.br/CEI_Responsivo/home.aspx'
        browser.get(url)
        
        inputElement = browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_txtLogin")
        inputElement.send_keys(cpf)
        inputElement = browser.find_element_by_id(
                "ctl00_ContentPlaceHolder1_txtSenha")
        inputElement.send_keys(password)
        inputElement.send_keys(Keys.RETURN)
           
        WebDriverWait(browser, 15).until(lambda browser:
            browser.current_url==
                'https://cei.b3.com.br/CEI_Responsivo/home.aspx')           
        
        
        url = 'https://cei.b3.com.br/CEI_Responsivo/'\
            'ConsultarMovimentoCustodia.aspx?TP_VISUALIZACAO=1'
        browser.get(url)
        
        tbody = browser.find_element_by_tag_name('table')\
            .find_element_by_tag_name('tbody')
        
        for tr in tbody.find_elements_by_tag_name('tr'):
            td_list = tr.find_elements_by_tag_name('td')
            data['Ticker'].append(td_list[2].text.strip())
            data['Quantidade'].append(int(td_list[5].text.strip()))
                
    except Exception as e:
        print(e)
        raise e
    finally:
        browser.quit()
    
    return data

def get_tickers_price(ticker_list):    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'\
            ' AppleWebKit/537.36 (KHTML, like Gecko)'\
                ' Chrome/39.0.2171.95 Safari/537.36'
    }
    prices = []
    regex = re.compile('.+Venda = .+')
    for ticker in ticker_list:
            url = 'http://www.grafbolsa.net/cgi-bin/al.pl/' + ticker.lower()
            r = requests.get(url,headers=headers)
            soup = BeautifulSoup(r.text)
            prices.append(float(soup.find(text=regex)\
                                    .split('Venda = ')[1].strip()))     
    return prices