from django.test import TestCase, TransactionTestCase 
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache

import pandas as pd 

from rebalanceamento import views
from rebalanceamento import planner
from rebalanceamento import tickerData
from rebalanceamento import forms

testFilePath = 'rebalanceamento/testInputs/'

def getFileData(fileName):
    with open(testFilePath + fileName,'rb') as f:
        return SimpleUploadedFile(f.name,f.read())

def submitFile(fileName):
    fileData = getFileData(fileName)
    return forms.WalletDataForm({},{'file':fileData}).is_valid()

# Create your tests here.
class PlannerTestCase(TestCase):
    def test_computePlanRebalance(self):
        data = {
            'Ticker': ['A', 'A2'],
            'PorcentagemAlvo': [25, 75],
            'Preço': [1, 1],
            'Quantidade': [25, 25],
            'PVP': [1, 1],
        }
        capital = 50
        
        plan, nonAllocatedCapital, waitFor = planner.computePlan(
            pd.DataFrame(data),
            capital
        )
        
        plan.set_index('Ticker', inplace=True)
        planLoc = plan.loc[
            'A2',
            'QuantidadeParaComprar'
        ]
        self.assertEqual(50, planLoc)
        self.assertEqual(50, plan['distance'].abs().sum())
        self.assertEqual(
            0, plan['distancePlanned'].abs().sum()
        )
        self.assertEqual(0, nonAllocatedCapital)

    def test_computePlanWaitFor(self):
        data = {
            'Ticker': ['A', 'A2'],
            'PorcentagemAlvo': [50, 50],
            'Preço': [1, 1100],
            'Quantidade': [1, 0],
            'PVP': [1, 1],
        }
        capital = 50
        
        plan, nonAllocatedCapital, waitFor = planner.computePlan(
            pd.DataFrame(data),
            capital
        )

        self.assertEqual(waitFor, 'A2')
        self.assertEqual(capital, nonAllocatedCapital)

    def test_computePlanNoAllocation(self):
        data = {
            'Ticker': ['A', 'A2', 'A3'],
            'PorcentagemAlvo': [33, 33, 33],
            'Preço': [1, 1, 50],
            'Quantidade': [15, 15, 0],
            'PVP': [1, 1, 1],
        }
        capital = 25
        
        plan, nonAllocatedCapital, waitFor = planner.computePlan(
            pd.DataFrame(data),
            capital
        )
        
        plan.set_index('Ticker', inplace=True)
        self.assertEqual(capital, nonAllocatedCapital)
        self.assertEqual(
            plan['distancePlanned'].abs().sum(),
            plan['distance'].abs().sum()
        )
    
    def test_computePlanInvest(self):
        data = {
            'Ticker': ['A', 'A2', 'A3'],
            'PorcentagemAlvo': [33, 33, 33],
            'Preço': [15, 23, 50],
            'Quantidade': [15, 15, 0],
            'PVP': [1, 1, 1],
        }
        capital = 2500
        
        plan, nonAllocatedCapital, waitFor = planner.computePlan(
            pd.DataFrame(data),capital
        )
        
        plan.set_index('Ticker', inplace=True)
        self.assertTrue(nonAllocatedCapital >= 0)
        self.assertTrue(
            plan['distancePlanned'].abs().sum()
            <= plan['distance'].abs().sum()
        )
        allocatedCapitalSeries = plan['QuantidadeParaComprar'] * plan['Preço']
        allocatedCapital = allocatedCapitalSeries.sum()
        totalCapital = nonAllocatedCapital + allocatedCapital
        self.assertEqual(totalCapital, capital)

class TickerDataTestCase(TestCase):    
    def test_findTickerInfoSuccess(self):
        # pull first ticker from fundamentus
        
        ticker = tickerData.getAValidTickerCode()
        tickerInfo = tickerData.getTickerInfo(ticker)

        self.assertTrue(set(['ticker','vpa','pvp','price']) == set(tickerInfo.keys()))
        self.assertTrue(type(tickerInfo['price']) == float)
        self.assertTrue(type(tickerInfo['pvp']) == float)
        self.assertTrue(type(tickerInfo['vpa']) == float)

    def test_findTickerInfoFail(self):
        self.assertIsNone(tickerData.getTickerInfo(''))
        self.assertIsNone(tickerData.getTickerInfo('QWEWEW'))

class FormTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        validTicker = tickerData.getAValidTickerCode(1)
        data1 = {
            'ticker': validTicker,
            'price': 1.1,
            'vpa': 1.1,
            'pvp': 1.1,
        }
        validTicker = tickerData.getAValidTickerCode(2)
        data2 = {
            'ticker': validTicker,
            'price': 1.1,
            'vpa': 1.1,
            'pvp': 1.1,
        }
        cache.set(data1['ticker'], data1, timeout=None)
        cache.set(data2['ticker'], data2, timeout=None)
        cls.stock1 = data1['ticker']
        cls.stock2 = data2['ticker']

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()

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
        walletForm = forms.createWalletPlanningForm(
            pd.DataFrame({'Ticker':['A','B'], 'Quantidade':[0, 0]})
        )

        fieldList = [
            'ticker',
            'quantity','percent'
        ]
        formFieldList = []
        for form in walletForm.forms:
            formFieldList+= list(form.base_fields.keys())
        
        self.assertTrue(
            set(fieldList) == set(formFieldList)
        )
    
    def test_createWalletPlanningFormSuccess(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': self.stock1,
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = walletForm(data)
        self.assertTrue(form.is_valid())

    def test_createWalletPlanningFormCleanFailureCapital(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':0,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': self.stock1,
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = forms.CapitalForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailureManagement(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': self.stock2,
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = walletForm(data)
        self.assertRaises(ValidationError,form.is_valid)

    def test_createWalletPlanningFormPOSTFailureQuantity(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '-2', 
            'form-0-percent': '50',
            'form-1-ticker': self.stock2,
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailurePercentAbove(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': self.stock2,
            'form-1-quantity': '2', 
            'form-1-percent': '51',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailurePercentBelow(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': self.stock2,
            'form-1-quantity': '2', 
            'form-1-percent': '-50',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailurePercentBelowNotFilled(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-1-ticker': self.stock2,
            'form-1-quantity': '2', 
            'form-1-percent': '-50',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailurePercentFill(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': self.stock2,
            'form-1-quantity': '2', 
        } 
        form = walletForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data[1]['percent'], 50)

    def test_createWalletPlanningFormPOSTFailureTicker(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': '',
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

class ViewTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        validTicker = tickerData.getAValidTickerCode(1)
        data1 = {
            'ticker': validTicker,
            'price': 1.1,
            'vpa': 1.1,
            'pvp': 1.1,
        }
        validTicker = tickerData.getAValidTickerCode(2)
        data2 = {
            'ticker': validTicker,
            'price': 1.1,
            'vpa': 1.1,
            'pvp': 1.1,
        }
        cache.set(data1['ticker'], data1, timeout=None)
        cache.set(data2['ticker'], data2, timeout=None)
        cls.stock1 = data1['ticker']
        cls.stock2 = data2['ticker']

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()


    def test_homeGET(self):
        response = self.client.get(
            reverse('home')
        )
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertTrue(
            'rebalanceamento/home.html' in templateList
        )
    
    def test_homePOSTSuccess(self):
        data = {'file':getFileData('valid.csv')}
        response = self.client.post(
            reverse('home'), 
            data
        )
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertTrue(
            'rebalanceamento/confirmWallet.html' in templateList
        )

    def test_viewHomePOSTFailure(self):
        data = {'file':getFileData('invalidType.txt')}
        response = self.client.post(
            reverse('home'), data
        )
        templateList = [
            template.name \
             for template in response.templates
        ]
        self.assertTrue(
            'rebalanceamento/confirmWallet.html' in templateList
        )

    def test_confirmWalletGET(self):
        response = self.client.get(reverse('confirmWallet'))
        templateList = [
            template.name \
             for template in response.templates
        ]
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in templateList
        )
    
    def test_confirmWalletPOSTSuccess(self):
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '100',
        } 
        response = self.client.post(reverse('confirmWallet'), data)
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertTrue(
            'rebalanceamento/plotPlan.html' in templateList
        )
    
    def test_confirmWalletPOSTFormFailure(self):
        data = {
            'capital': '0',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '100',
        }
        response = self.client.post(reverse('confirmWallet'), data)
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertFalse(
            'rebalanceamento/plotPlan.html' in templateList
        )

    def test_confirmWalletPOSTFormInvalidForm(self):
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '1',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '100',
        } 
        response = self.client.post(
            reverse('confirmWallet'), 
            data)
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertFalse(
            'rebalanceamento/plotPlan.html' in templateList
        )

    def test_redoWalletGET(self):
        response = self.client.get(
            reverse('redoWallet'))
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in templateList
        )

    def test_redoWalletPOSTSuccess(self):
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '100',
        } 
        response = self.client.post(
            reverse('redoWallet'), data
        )
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertTrue(
            'rebalanceamento/confirmWallet.html' in templateList
        )

    def test_redoWalletPOSTFailure(self):
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '102',
        } 
        response = self.client.post(
            reverse('redoWallet'), 
            data
        )
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in templateList
        )

    def test_redoWalletPOSTInvalidForm(self):
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '1',
            'form-0-ticker': self.stock1,
            'form-0-quantity': '2', 
            'form-0-percent': '100',
        } 
        response = self.client.post(
            reverse('redoWallet'), data
        )
        templateList = [
            template.name \
            for template in response.templates
        ]
        self.assertFalse(
            'rebalanceamento/confirmWallet.html' in templateList
        )
    