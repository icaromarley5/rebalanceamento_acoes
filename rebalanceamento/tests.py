from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import pandas as pd 
from selenium import webdriver
import time

from rebalanceamento import views
from rebalanceamento import planner
from rebalanceamento import tickerData
from rebalanceamento import forms
from rebalanceamento import cleaner
from rebalanceamento import loginInfo

# Create your tests here.
class PlannerTestCase(TestCase):
    def test_computePlanRebalance(self):
        data = {
            'Ticker': ['A', 'A2'],
            '% alvo': [25, 75],
            'Preço': [1, 1],
            'Quantidade': [25, 25],
            }
        capital = 50
        
        plan, nonAllocatedCapital = planner.computePlan(
            pd.DataFrame(data),
            capital)
        
        plan.set_index('Ticker', inplace=True)
        self.assertEqual(50, plan.loc[
            'A2',
            'Quantidade para comprar'])
        self.assertEqual(50, plan['distance'].abs().sum())
        self.assertEqual(0, 
            plan['distancePlanned'].abs().sum())
        self.assertEqual(0, nonAllocatedCapital)
    
    def test_computePlanNoAllocation(self):
        data = {
            'Ticker': ['A', 'A2', 'A3'],
            '% alvo': [33, 33, 33],
            'Preço': [1, 1, 50],
            'Quantidade': [15, 15, 0],
            }
        capital = 25
        
        plan, nonAllocatedCapital = planner.computePlan(
            pd.DataFrame(data),
            capital)
        
        plan.set_index('Ticker', inplace=True)
        self.assertEqual(capital, nonAllocatedCapital)
        self.assertEqual(
            plan['distancePlanned'].abs().sum(),
            plan['distance'].abs().sum())
    
    def test_computePlanInvest(self):
        data = {
            'Ticker': ['A', 'A2', 'A3'],
            '% alvo': [33, 33, 33],
            'Preço': [15, 23, 50],
            'Quantidade': [15, 15, 0],
            }
        capital = 2500
        
        plan, nonAllocatedCapital = planner.computePlan(
            pd.DataFrame(data),capital)
        
        plan.set_index('Ticker', inplace=True)
        self.assertTrue(nonAllocatedCapital >= 0)
        self.assertTrue(
            plan['distancePlanned'].abs().sum()
            <= plan['distance'].abs().sum())
        totalCapital = nonAllocatedCapital \
            + (plan['Quantidade para comprar'] \
               * plan['Preço']).sum()
        self.assertEqual(totalCapital, capital)

     
class TickerDataTestCase(TestCase):
    def testLoadBrowser(self):
        tickerData.threadCreateBrowser.join()
        self.assertTrue(isinstance(tickerData.browser,
                                   webdriver.Chrome))
        
    def test_getTickersPriceSuccess(self):
        tickerList = ['ABEV3', 'MDIA3',
                       'MGLU3', 'ITUB4', 'NTCO3']
        priceList = tickerData._getTickersPrice(tickerList)
        self.assertFalse(any(map(
            lambda x: x == 0, priceList)))
        try:
            priceList = map(float, priceList)
        except:
            pass
        self.assertTrue(all(map(
            lambda x: isinstance(x, float), priceList)))

    def test_getTickersPriceFail(self):
        with self.assertRaisesMessage(Exception,
                                      'Data not found'):
            tickerList = ['']
            tickerData._getTickersPrice(tickerList)

    def test_getCEIdataFail(self):
        with self.assertRaisesMessage(Exception,
                                      'Data not found'):
            tickerData._getCEIdata('a', 'a')

    def test_getCEIdataSuccess(self):
        cpf = loginInfo.cpf
        password = loginInfo.password
        data = tickerData._getCEIdata(cpf, password)

        self.assertTrue(all(map(
            lambda x: isinstance(x, str),
            data['Ticker'])))
        self.assertTrue(all(map(
            lambda x: x == x.upper(),
            data['Ticker'])))
        self.assertTrue(all(map(
            lambda x: isinstance(x,int),
            data['Quantidade'])))

class FormTestCase(TestCase):
    def test_CEIformclean(self):
        data = {
            'cpf': '1',
            'password': '1',
            'accept': False
            }
        form = forms.CEIForm(data=data)
        self.assertEqual(False, form.is_valid())
        
    def test_createWalletForm(self):
        data = {
            'Ticker': ['A', 'B', 'C'],
            'Quantidade':[0, 0, 0],
            'Preço': [0, 0, 0],
            }
        WalletForm = forms.createWalletForm(data)
        
        n = len(data['Ticker'])
        fieldList = ['capital']
        fieldList += ['price'+str(i) for i in range(n)]
        fieldList += ['ticker'+str(i) for i in range(n)]
        fieldList += ['quantity'+str(i) for i in range(n)]
        fieldList += ['percent'+str(i) for i in range(n)]
        
        self.assertTrue(
            set(fieldList)
            == set(WalletForm.base_fields.keys()))
   
    def test_WalletFormClean(self):
        data = {
            'Ticker': ['A', 'B'],
            'Quantidade': [0, 0],
            'Preço': [0, 0],
            }
        WalletForm = forms.createWalletForm(data)
        
        data = {
            'capital': 0,
            'ticker0': 'a',
            'ticker1': 'b',
            'quantity0': 0,
            'quantity1': 0,
            'percent0': 50,
            'percent1': 50,
            'price0': 1,
            'price1': 4,
            }
        
        form = WalletForm(data)
        self.assertFalse(form.is_valid())
        
        data = {
            'capital': 1,
            'ticker0': 'a',
            'ticker1': 'b',
            'quantity0': 0,
            'quantity1': 0,
            'percent0': 50,
            'percent1': 50,
            'price0': 1,
            'price1': 4,
            }
        form = WalletForm(data)
        self.assertTrue(form.is_valid())

        data = {
            'capital':1,
            'ticker0':'a',
            'ticker1':'b',
            'quantity0':0,
            'quantity1':0,
            'percent0':50,
            'percent1':50,
            'price0':0,
            'price1':4,
            }
        form = WalletForm(data)
        self.assertFalse(form.is_valid())

class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
  
    def test_viewHome(self):
        cpf = '2'
        password = cpf
        response = self.client.post(
            reverse('home'), {
                'cpf': cpf, 
                'password': password,
                'accept': True})
        self.assertTrue(
            'rebalanceamento/loading.html' in 
            [template.name 
             for template in response.templates])
    
    def test_checkResultsFailSuccessQueue(self):
        cpf = '3'
        password = cpf
        response = self.client.post(
            reverse('home'), {
                'cpf': cpf, 
                'password': password,
                'accept':True})
        response = self.client.get(reverse(
            'checkResults',
            kwargs={'cpf':cpf}))
        self.assertEqual(response.content, b'Fail')
   
        self.client.post(
            reverse('home'), {
                'cpf': loginInfo.cpf, 
                'password': loginInfo.password,
                'accept': True})
        response = self.client.get(
            reverse(
                'checkResults',
                kwargs={'cpf': loginInfo.cpf}))
        self.assertEqual(response.content, b'Success')

    def test_confirmWalletPlotPlan(self):
        self.client.post(reverse('home'), {
            'cpf': loginInfo.cpf, 
            'password': loginInfo.password,
            'accept':True})
        response = self.client.get(
            reverse('checkResults',
                    kwargs={'cpf': loginInfo.cpf}))
        self.assertEqual(response.content, b'Success')
        
        response = self.client.get(
            reverse('confirmWallet', 
                    kwargs={'cpf': loginInfo.cpf}))
        self.assertTrue(
            'form' in response.context.keys() 
            and 'cpf' in response.context.keys())
        
        data = {
            'capital': 100,
        }
        form = response.context['form']
        total = 0
        fields = form.hidden_fields() + form.visible_fields()
        for field in fields:
            if field.html_name == 'capital': continue
            if 'percent' in field.html_name:
                total += field.value()
            data[field.html_name] = field.value()
        data['percent0'] += 100 - total

        response = self.client.post(
            reverse('confirmWallet',
                kwargs={'cpf': loginInfo.cpf}),data,
                follow= True)
        self.assertRedirects(response, 
            reverse(
                'plotPlan',
                kwargs={'cpf': loginInfo.cpf}))
        self.assertTrue(
            'allocationScript' in response.context.keys())

class TemplateTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = tickerData.createBrowser()
        cls.client = Client()
        
    def test_loadingJs(self):
        self.browser.get(
            self.live_server_url  + reverse('home'))        
        inputElement = self.browser.find_element_by_name(
                "cpf")
        inputElement.send_keys(loginInfo.cpf)
        inputElement = self.browser.find_element_by_name(
                "password")
        inputElement.send_keys(loginInfo.password)
        self.browser.find_element_by_class_name('btn').click()
        while 'Carregando dados do CEI' not in self.browser.page_source:
            time.sleep(.5)
        self.assertTrue('Carregando dados do CEI' in self.browser.page_source)

        while 'Carregando dados do CEI' in self.browser.page_source:
            time.sleep(.5)
        self.assertTrue('confirm' in self.browser.current_url)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

class CleanerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
  
    def test_cleaner(self):
        cpf = '5'
        password = cpf
        response = self.client.post(reverse('home'), 
                {'cpf': cpf, 
                 'password': password,
                 'accept': True})
        self.assertTrue('rebalanceamento/loading.html' in 
            [template.name for template in response.templates])
        self.assertTrue(tickerData.tickerOutputBuffer.get(
            cpf,None))
        time.sleep(60 * 5)
        self.assertEqual(tickerData.tickerOutputBuffer.get(
            cpf,None),None)