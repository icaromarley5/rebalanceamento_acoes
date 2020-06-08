from django.shortcuts import render, redirect
from .forms import CapitalForm, WalletDataForm, createWalletPlanningForm

from rebalanceamento import planner
from rebalanceamento import dataPlots
from rebalanceamento.tickerData import getTickerList

from dal import autocomplete

import logging

logger = logging.getLogger('rebalanceamento')

import pandas as pd

def home(request):
    if request.method == 'POST':
        form = WalletDataForm(request.POST, request.FILES)
        if form and form.is_valid():
            data = form.cleaned_data['file']
        else:
            dataDict = {
                'Ticker': [''],
                'Quantidade': [0],
                'Porcentagem alvo': [100],
            }
            data = pd.DataFrame(dataDict)
        form = createWalletPlanningForm(data)
        renderData = {
            'walletFormSet': form,
            'capitalForm':CapitalForm()
        }
        return render(
            request, 
            'rebalanceamento/confirmWallet.html', 
            renderData
        )
    form = WalletDataForm()
    renderData = {'form':form}
    return render(
        request, 
        'rebalanceamento/home.html', 
        renderData
    )

def redirect404(request, *args, **kwargs):
    return redirect('home')

def confirmWallet(request):    
    if request.method == 'POST':   
        capitalForm = CapitalForm(request.POST)
        WalletForm = createWalletPlanningForm()
        walletForm = WalletForm(request.POST)
        try:
            valid = capitalForm.is_valid() and walletForm.is_valid()
        except Exception as e:
            valid = False
            capitalForm = CapitalForm()
            WalletForm = createWalletPlanningForm()
            walletForm = WalletForm()
        if valid:
            df = pd.DataFrame(walletForm.cleaned_data)
            df.columns = ['Ticker', 'Quantidade', 'PorcentagemAlvo']
            df['VPA'] = df['Ticker'].apply(lambda x:x['vpa'])
            df['Preço'] = df['Ticker'].apply(lambda x:x['price'])
            df['PVP'] = df['Ticker'].apply(lambda x:x['pvp'])
            df['Ticker'] = df['Ticker'].apply(lambda x:x['ticker'])
            capital = capitalForm.cleaned_data['capital']
            plan, nonAllocatedCapital, waitFor = planner.computePlan(
                pd.DataFrame(df), capital
            )
            dataToPlot = {
                'plan': plan,
                'allocatedCapital': capital - nonAllocatedCapital,
                'nonAllocatedCapital': nonAllocatedCapital
            }
            data = {'waitFor':waitFor}

            data.update(dataPlots.createPlots(dataToPlot))
            data['capitalForm'] = capitalForm
            data['walletFormSet'] = walletForm
            return render(
                request, 
                'rebalanceamento/plotPlan.html',
                data
            ) 
        dataRender = {
            'walletFormSet': walletForm, 
            'capitalForm': capitalForm
        }
        return render(
            request, 
            'rebalanceamento/confirmWallet.html', 
            dataRender
        )
    return redirect('home') 

def redoWallet(request):
    if request.method == 'POST':
        capitalForm = CapitalForm(request.POST)
        WalletForm = createWalletPlanningForm()
        walletForm = WalletForm(request.POST)
        try:
            valid = capitalForm.is_valid() and walletForm.is_valid()
        except:
            valid = False
        if valid:
            dataRender = {
                'walletFormSet': walletForm,
                'capitalForm': capitalForm
            }
            return render(
                request, 
                'rebalanceamento/confirmWallet.html',
                dataRender
            )
    return redirect('home')
        
class StockAutocomplete(autocomplete.Select2ListView):
    def get_list(self):
        return getTickerList()