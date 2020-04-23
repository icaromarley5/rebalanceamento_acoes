from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CapitalForm, WalletDataForm, createWalletPlanningForm

from rebalanceamento import planner
from rebalanceamento import dataPlots
from rebalanceamento.models import Stock

import pandas as pd

import logging

logger = logging.getLogger(__name__)

def home(request):
    if request.method == 'POST':
        form = WalletDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data['file']
            form = createWalletPlanningForm(data)
            return render(request, 
                          'rebalanceamento/confirmWallet.html',{
                              'walletFormSet': form,
                              'capitalForm':CapitalForm()})
    else:
        form = WalletDataForm()
    return render(request, 
                  'rebalanceamento/home.html',{
                      'form':form})

def confirmWallet(request):    
    if request.method == 'POST':        
        capitalForm = CapitalForm(request.POST)
        WalletForm = createWalletPlanningForm()
        walletForm = WalletForm(request.POST)
        if capitalForm.is_valid() and walletForm.is_valid():
            df = pd.DataFrame(walletForm.cleaned_data)
            df.columns = ['Ticker','Quantidade','PorcentagemAlvo']
            stockList = [Stock.getOrCreate(ticker) for ticker in df['Ticker']]
            df['VPA'] = [stock.vpa for stock in stockList]
            df['Preço'] = [stock.price for stock in stockList]
            capital = capitalForm.cleaned_data['capital']
            plan, nonAllocatedCapital = planner.computePlan(
                pd.DataFrame(df), capital)
            dataToPlot = {
                    'plan': plan,
                    'allocatedCapital': capital - nonAllocatedCapital,
                    'nonAllocatedCapital': nonAllocatedCapital, }
            plots = dataPlots.createPlots(dataToPlot)
            return render(
                request, 
                'rebalanceamento/plotPlan.html',
                plots) 
        return render(
            request, 
            'rebalanceamento/confirmWallet.html',
            {'walletFormSet': walletForm,'capitalForm':capitalForm})
    return redirect('home') 

'''
def confirmWallet(request):    
    dataToPlot = {
            'plan': pd.read_csv('planTest.csv'),
            'capital': 123.0,
            'nonAllocatedCapital': 26.42,
        }
    plots = dataPlots.createPlots(dataToPlot)
    return render(
        request, 
        'rebalanceamento/plotPlan.html',
        plots) 
'''



"""
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import WalletDataForm, createWalletPlanningForm, createWalletPlanningFormPOST

from rebalanceamento import planner
from rebalanceamento import dataPlots
from rebalanceamento.models import Stock

import pandas as pd

import logging

logger = logging.getLogger(__name__)

def home(request):    
    if request.method == 'POST':
        form = WalletDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data['file']
            formClass = createWalletPlanningForm(data)
            form = formClass()
            return render(request, 
                          'rebalanceamento/confirmWallet.html',
                          {'form': form})    
    else:
        form = WalletDataForm()
    return render(request, 
                  'rebalanceamento/home.html',
                  {'form': form})

def confirmWallet(request):    
    if request.method == 'POST':
        postData = {}
        for key, items in request.POST.items():
            postData[key] = items[0] if type(items) is list else items
        formClass = createWalletPlanningFormPOST(postData)
        if formClass:
            form = formClass(request.POST)
            if form.is_valid():
                nRows = (len(form.cleaned_data)-1) // 3
                df = pd.DataFrame([])
                df['Ticker'] = [form.cleaned_data['ticker' + str(i)] for i in range(nRows)]
                df['Quantidade'] = [form.cleaned_data['quantity' + str(i)] for i in range(nRows)]
                df['PorcentagemAlvo']  = [form.cleaned_data['percent' + str(i)] for i in range(nRows)]               
                
                stockList = [Stock.getOrCreate(ticker) for ticker in df['Ticker']]
                if None in stockList:
                    return redirect('home') 
                
                df['VPA'] = [stock.vpa for stock in stockList]
                df['Preço'] = [stock.price for stock in stockList]

                capital = form.cleaned_data['capital']
                plan, nonAllocatedCapital = planner.computePlan(
                    pd.DataFrame(df), capital)
                dataToPlot = {
                        'plan': plan,
                        'allocatedCapital': capital - nonAllocatedCapital,
                        'nonAllocatedCapital': nonAllocatedCapital, }

                plots = dataPlots.createPlots(dataToPlot)
                return render(
                    request, 
                    'rebalanceamento/plotPlan.html',
                    plots) 
            return render(
                request, 
                'rebalanceamento/confirmWallet.html',
                {'form': form})
    return redirect('home') 

'''
def confirmWallet(request):    
    dataToPlot = {
            'plan': pd.read_csv('planTest.csv'),
            'capital': 123.0,
            'nonAllocatedCapital': 26.42,
        }
    plots = dataPlots.createPlots(dataToPlot)
    return render(
        request, 
        'rebalanceamento/plotPlan.html',
        plots) 
'''"""