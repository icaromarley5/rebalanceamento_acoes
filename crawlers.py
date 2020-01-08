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

def get_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1366x1280")
    
    return webdriver.Chrome(chrome_options=chrome_options)
    
def get_cei_data(cpf,password,cod):
    data = {
        'Ticket':[],
        'Quantidade':[],
    }
    
    browser = get_browser()
   
    try:
        url = 'https://cei.b3.com.br/CEI_Responsivo/negociacao-de-ativos.aspx'
        browser.get(url)
        
        inputElement = browser.find_element_by_id("ctl00_ContentPlaceHolder1_txtLogin")
        inputElement.send_keys(cpf)
        inputElement = browser.find_element_by_id("ctl00_ContentPlaceHolder1_txtSenha")
        inputElement.send_keys(password)
        inputElement.send_keys(Keys.RETURN)
        
        WebDriverWait(browser,10).until(lambda driver:driver.current_url=='https://cei.b3.com.br/CEI_Responsivo/home.aspx')           
        
        browser.get(url)
        
        selectElement = browser.find_element_by_id('ctl00_ContentPlaceHolder1_ddlAgentes')
        
        select = Select(selectElement)
        
        for o in select.options:
            value = o.get_attribute('value')
            if cod in value:
                select.select_by_value(value)
                selectElement.submit()
                break
        WebDriverWait(browser,10).until(lambda driver:driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlContas').get_attribute('value') != '')           
        
        browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnConsultar').click()
        WebDriverWait(browser,10).until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_pnResumoNegocios")))           
        
        table_info = browser.find_element_by_id('ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_pnResumoNegocios').find_element_by_tag_name('tbody')
        
        for tr in table_info.find_elements_by_tag_name('tr'):
            td_list = tr.find_elements_by_tag_name('td')
            data['Ticket'].append(td_list[0].text)
            data['Quantidade'].append(int(td_list[6].text))

    except Exception as e:
        raise e
    finally:
        browser.quit()
    
    return data


def get_tickets_price(ticket_list):
    price_list = []
    url = 'https://br.tradingview.com/symbols/BMFBOVESPA-{}/'
    
    browser = get_browser()

    for ticket in ticket_list:
        browser.get(url.format(ticket))
        x_path = "//div[@class='tv-symbol-price-quote__value js-symbol-last']/span"
        WebDriverWait(browser,10).until(lambda driver:driver.find_element_by_xpath(x_path).text != '') 
        price = float(browser.find_element_by_xpath("//div[@class='tv-symbol-price-quote__value js-symbol-last']/span").text)
        price_list.append(price)
    browser.quit()
    
    return price_list