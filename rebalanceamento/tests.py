from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django.core.files.uploadedfile import SimpleUploadedFile

import pandas as pd 
import time

import requests
from bs4 import BeautifulSoup

from rebalanceamento import views
from rebalanceamento import planner
from rebalanceamento import tickerData
from rebalanceamento import forms

testFilePath = 'rebalanceamento/testInputs/'

'''
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

def getTickerCode():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'\
        ' AppleWebKit/537.36 (KHTML, like Gecko)'\
        ' Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get('https://www.fundamentus.com.br/detalhes.php',headers=headers)
    soup = BeautifulSoup(r.text)
    return soup.find('td').text.strip()

def checkProcessingEmpty(fileName):
    return tickerData.processCSV(testFilePath + fileName).empty

class TickerDataTestCase(TestCase):
    def test_processCSVSuccess(self):
        self.assertFalse(checkProcessingEmpty('valid.csv'))

    def test_processCSVFailHeader(self):
        self.assertTrue(checkProcessingEmpty('invalidHeader.csv'))

    def test_processCSVFailQuantity(self):
        self.assertTrue(checkProcessingEmpty('invalidQuantity.csv'))

    def test_processCSVFailStructure(self):
        self.assertTrue(checkProcessingEmpty('invalidStructure.csv'))

    def test_processCSVFailTicker(self):
        self.assertTrue(checkProcessingEmpty('invalidTicker.csv'))

    def test_processCSVFailTicker2(self):
        self.assertTrue(checkProcessingEmpty('invalidTicker2.csv'))
    
    def test_addTickerInfoSuccess(self):
        # pull first ticker from fundamentus
        
        data = {'Ticker':[getTickerCode()]}
        dataImproved = tickerData.addTickerInfo(data)

        self.assertTrue('Preço' in dataImproved.keys() and 'VPA' in dataImproved.keys())
        self.assertTrue(type(dataImproved['Preço'][0]) == float)
        self.assertTrue(type(dataImproved['VPA'][0]) == float)

    def test_addTickerInfoFail(self):
        with self.assertRaisesMessage(Exception,
                                      'Data not found'):
            data = {'Ticker':[]}
            tickerData.addTickerInfo(data)
        with self.assertRaisesMessage(Exception,
                                      'Data not found'):
            data = {'Ticker':['QWEWEW']}
            tickerData.addTickerInfo(data)
'''

def getFileData(fileName):
    with open(testFilePath + fileName,'rb') as f:
        return SimpleUploadedFile(f.name,f.read())

def submitFile(fileName):
    fileData = getFileData(fileName)
    return forms.WalletDataForm({},{'file':fileData}).is_valid()
'''
class FormTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = pd.DataFrame({
            'Ticker': ['A', 'B'],
            'Quantidade': [0, 0]})
        cls.WalletForm = forms.createWalletPlanningForm(cls.data)

    def test_WalletDataFormTypeSuccess(self):
        self.assertTrue(submitFile('valid.csv'))

    def test_WalletDataFormTypeFail(self):
        self.assertFalse(submitFile('invalidType.txt'))

    def test_WalletDataFormHeaderFail(self):
        self.assertFalse(submitFile('invalidHeader.csv'))

    def test_WalletDataFormQuantityFail(self):
        self.assertFalse(submitFile('invalidQuantity.csv'))

    def test_WalletDataFormStructureFail(self):
        self.assertFalse(submitFile('invalidStructure.csv'))

    def test_WalletDataFormTickerFail(self):
        self.assertFalse(submitFile('invalidTicker.csv'))

    def test_WalletDataFormTicker2Fail(self):
        self.assertFalse(submitFile('invalidTicker2.csv'))

    def test_createWalletPlanningForm(self):
        n = self.data.shape[0]
        fieldList = ['capital']
        fieldList += ['ticker' + str(i) for i in range(n)]
        fieldList += ['quantity' + str(i) for i in range(n)]
        fieldList += ['percent' + str(i) for i in range(n)]
        
        self.assertTrue(
            set(fieldList)
            == set(self.WalletForm.base_fields.keys()))
        
    def test_createWalletPlanningFormCapitalCleanSuccess(self):
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
        form = self.WalletForm(data)
        self.assertTrue(form.is_valid())

    def test_createWalletPlanningFormCleanFailureCapital(self):
        data = {
            'capital': 0,
            'ticker0': 'a',
            'ticker1': 'b',
            'quantity0': 0,
            'quantity1': 0,
            'percent0': 50,
            'percent1': 50,
            }
        
        form = self.WalletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormCapitalCleanFailurePercent(self):
        data = {
            'capital':1,
            'ticker0':'a',
            'ticker1':'b',
            'quantity0':0,
            'quantity1':0,
            'percent0':50,
            'percent1':49,
            }
        form = self.WalletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormPOSTSuccess(self):
        data = {
            'ticker0':'ABEV3',
            'quantity0':0,
            'percent0':100,
            'capital':100,
            'tokenForm':'',
        } 
        self.assertIsNotNone(forms.createWalletPlanningFormPOST(data))

    def test_createWalletPlanningFormPOSTFailureSize(self):
        data = {
            'ticker0':'ABEV3',
            'quantity0':0,
            'percent0':100,
            'tokenForm':'',
        } 
        self.assertIsNone(forms.createWalletPlanningFormPOST(data))

    def test_createWalletPlanningFormPOSTFailureSize2(self):
        data = {
            'ticker0':'ABEV3',
            'ticker1':'ABEV3',
            'quantity0':0,
            'percent0':100,
            'capital':100,
            'tokenForm':'',
        } 
        self.assertIsNone(forms.createWalletPlanningFormPOST(data))

    def test_createWalletPlanningFormPOSTFailureField(self):
        data = {
            'ticke2r0':'ABEV3',
            'quantity0':0,
            'percent0':100,
            'capital':100,
            'tokenForm':'',
        } 
        self.assertIsNone(forms.createWalletPlanningFormPOST(data))
'''

class ViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
    
    def test_viewHomeGET(self):
        response = self.client.get(
            reverse('home'))
        self.assertTrue(
            'rebalanceamento/home.html' in 
            [template.name 
             for template in response.templates])

    def test_viewHomePOSTSuccess(self):
        response = self.client.post(
            reverse('home'), {'file':getFileData('valid.csv')})
        self.assertTrue(
            'rebalanceamento/confirmWallet.html' in 
            [template.name 
             for template in response.templates])

    def test_viewHomePOSTFailure(self):
        response = self.client.post(
            reverse('home'), {'file':getFileData('invalidType.txt')})
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in 
            [template.name 
             for template in response.templates])

    def test_confirmWalletGET(self):
        response = self.client.get(reverse('confirmWallet'))
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in 
            [template.name 
             for template in response.templates])

    def test_confirmWalletPOSTSuccess(self):
        data = {
            'ticker0':'ABEV3',
            'quantity0':0,
            'percent0':100,
            'capital':100,
            'tokenForm':'',
        } 
        response = self.client.post(reverse('confirmWallet'), data)
        
        self.assertTrue(
            'rebalanceamento/plotPlan.html' in 
            [template.name 
             for template in response.templates])

    def test_confirmWalletPOSTWalletCreationFailure(self):
        data = {
            'ticker0':'ABEV3',
            'percent0':100,
            'capital':100,
            'tokenForm':'',
        } 
        response = self.client.post(reverse('confirmWallet'), data)
        
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in 
            [template.name 
             for template in response.templates])

    def test_confirmWalletPOSTFormFailure(self):
        data = {
            'ticker0':'ABEV3',
            'quantity0':0,
            'percent0':100,
            'capital':0,
            'tokenForm':'',
        } 
        response = self.client.post(reverse('confirmWallet'), data)
        
        self.assertTrue(
            'rebalanceamento/confirmWallet.html' in 
            [template.name 
             for template in response.templates])

    def test_confirmWalletPOSTFormFailure(self):
        data = {
            'ticker0':'AAAA3',
            'quantity0':0,
            'percent0':100,
            'capital':100,
            'tokenForm':'',
        } 
        response = self.client.post(reverse('confirmWallet'), data)
        
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in 
            [template.name 
             for template in response.templates])