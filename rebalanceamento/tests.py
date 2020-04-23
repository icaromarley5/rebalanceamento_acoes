from django.test import TestCase, TransactionTestCase 
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.exceptions import ValidationError

import pandas as pd 

from rebalanceamento import views
from rebalanceamento import planner
from rebalanceamento import tickerData
from rebalanceamento import forms
from rebalanceamento.models import Stock

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
            }
        capital = 50
        
        plan, nonAllocatedCapital = planner.computePlan(
            pd.DataFrame(data),
            capital)
        
        plan.set_index('Ticker', inplace=True)
        self.assertEqual(50, plan.loc[
            'A2',
            'QuantidadeParaComprar'])
        self.assertEqual(50, plan['distance'].abs().sum())
        self.assertEqual(0, 
            plan['distancePlanned'].abs().sum())
        self.assertEqual(0, nonAllocatedCapital)
    
    def test_computePlanNoAllocation(self):
        data = {
            'Ticker': ['A', 'A2', 'A3'],
            'PorcentagemAlvo': [33, 33, 33],
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
            'PorcentagemAlvo': [33, 33, 33],
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
            + (plan['QuantidadeParaComprar'] \
               * plan['Preço']).sum()
        self.assertEqual(totalCapital, capital)

class TickerDataTestCase(TestCase):    
    def test_findTickerInfoSuccess(self):
        # pull first ticker from fundamentus
        
        ticker = tickerData.getAValidTickerCode()
        tickerInfo = tickerData.findTickerInfo(ticker)

        self.assertTrue(set(['Ticker','VPA','Preço','Nome']) == set(tickerInfo.keys()))
        self.assertTrue(type(tickerInfo['Preço']) == float)
        self.assertTrue(type(tickerInfo['VPA']) == float)
        self.assertTrue(tickerInfo['Nome'])

    def test_findTickerInfoFail(self):
        self.assertIsNone(tickerData.findTickerInfo(''))
        self.assertIsNone(tickerData.findTickerInfo('QWEWEW'))

class FormTestCase(TestCase):
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
            pd.DataFrame({'Ticker':['A','B'],'Quantidade':[0,0]})
        )

        fieldList = [
            'ticker',
            'quantity','percent']
        formFieldList = []
        for form in walletForm.forms:
            formFieldList+= list(form.base_fields.keys())
        
        self.assertTrue(
            set(fieldList) == set(formFieldList))
    
    def test_createWalletPlanningFormSuccess(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': 'ITUB3',
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
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': 'ITUB3',
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = forms.CapitalForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailurePercentTotal(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': 'ITUB3',
            'form-1-quantity': '2', 
            'form-1-percent': '51',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailureManagement(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': 'ITUB3',
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
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '-2', 
            'form-0-percent': '50',
            'form-1-ticker': 'ITUB3',
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormFailurePercent(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': 'ITUB3',
            'form-1-quantity': '2', 
            'form-1-percent': '-50',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

    def test_createWalletPlanningFormPOSTFailureTicker(self):
        walletForm = forms.createWalletPlanningForm()
        data = {
            'capital':100,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '50',
            'form-1-ticker': '',
            'form-1-quantity': '2', 
            'form-1-percent': '50',
        } 
        form = walletForm(data)
        self.assertFalse(form.is_valid())

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
            'capital':100,
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '100',
        } 
        response = self.client.post(reverse('confirmWallet'), data)
        
        self.assertTrue(
            'rebalanceamento/plotPlan.html' in 
            [template.name 
             for template in response.templates])

    def test_confirmWalletPOSTFormFailure(self):
        data = {
            'capital': '0',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-ticker': 'ABEV3',
            'form-0-quantity': '2', 
            'form-0-percent': '100',
        }
        response = self.client.post(reverse('confirmWallet'), data)
        
        self.assertFalse(
            'rebalanceamento/plotPlan.html' in 
            [template.name 
             for template in response.templates])


class ModelTestCase(TransactionTestCase ):
    def test_StockgetOrCreateStockOOSCurrentInvalid(self):
        ticker = ''
        yesterday = (timezone.now() - timezone.timedelta(days=1)).date()
        stock = Stock(
            ticker=ticker, name='Test', 
            vpa=1, price=1,
            day = yesterday)
        stock.save()
        stock = Stock.objects.get(ticker=ticker)
        self.assertEqual(yesterday, stock.day) 
        self.assertEqual(yesterday, stock.day)
        stockUpdated = Stock.getOrCreate(ticker)
        self.assertIsNone(stockUpdated)
        self.assertRaises(Stock.DoesNotExist, 
            lambda: Stock.objects.get(ticker=ticker))

    def test_StockgetOrCreateStockOOSValid(self):
        ticker = 'B3SA3'
        yesterday = (timezone.now() - timezone.timedelta(days=1)).date()
        stock = Stock(
            ticker=ticker, name='Test', 
            vpa=0, price=0,
            day=yesterday)
        stock.save()
        stock = Stock.objects.get(ticker=ticker)
        self.assertEqual(yesterday, stock.day) 
        self.assertEqual(yesterday, stock.day)
        stockUpdated = Stock.getOrCreate(ticker)
        self.assertIsNotNone(stockUpdated)
        self.assertNotEqual(stockUpdated.day, yesterday)
        self.assertNotEqual(stockUpdated.name, 'Test')
        self.assertNotEqual(stockUpdated.vpa, 0)
        self.assertNotEqual(stockUpdated.price, 0)

    def test_StockgetOrCreateStockSync(self):
        ticker = 'B3SA3'
        self.assertRaises(Stock.DoesNotExist, 
            lambda: Stock.objects.get(ticker=ticker))
        stockAdded = Stock.getOrCreate(ticker)
        self.assertIsNotNone(stockAdded)
        yesterday = (timezone.now() - timezone.timedelta(days=1)).date()
        self.assertNotEqual(stockAdded.day, yesterday)
        self.assertNotEqual(stockAdded.name, 'Test')
        self.assertNotEqual(stockAdded.vpa, 0)
        self.assertNotEqual(stockAdded.price, 0)

    def test_StockgetOrCreateStockNotAddedInvalid(self):
        ticker = ''
        self.assertRaises(Stock.DoesNotExist, 
            lambda: Stock.objects.get(ticker=ticker))
        stockAdded = Stock.getOrCreate(ticker)
        self.assertIsNone(stockAdded)