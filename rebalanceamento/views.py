from django.shortcuts import render, redirect
from .forms import CapitalForm, WalletDataForm, createWalletPlanningForm

from rebalanceamento import planner
from rebalanceamento import dataPlots

from django.db.models import Q
from dal import autocomplete

from rebalanceamento.models import Stock

import logging

logger = logging.getLogger('rebalanceamento')

from rebalanceamento import watcherDB

import pandas as pd

def home(request):
    if request.method == 'POST':
        form = WalletDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data['file']
        else:
            data = pd.DataFrame({
                'Ticker':[''],
                'Quantidade':[0]})
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
            df['VPA'] = df['Ticker'].apply(lambda x:x.vpa)
            df['Preço'] = df['Ticker'].apply(lambda x:x.price)
            df['Ticker'] = df['Ticker'].apply(lambda x:x.ticker)
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

class StockAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Stock.objects.all()

        if self.q:
            qs = qs.filter(
                Q(name__istartswith=self.q)|Q(ticker__istartswith=self.q))
        return qs