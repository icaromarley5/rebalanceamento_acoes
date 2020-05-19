from django import forms
from django.forms import formset_factory
from django.forms import BaseFormSet

from django.core.validators import FileExtensionValidator

from dal import autocomplete

import pandas as pd 
import numpy as np

from rebalanceamento.models import Stock

class WalletDataForm(forms.Form):
    file = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(['csv'])], 
        label='Arquivo CSV',
        widget=forms.FileInput(
            attrs={
                'class':'form-control-file border border-grey'
            }
        )
    )
 
    def clean_file(self):
        def processCSV(csvFile):
            df = pd.DataFrame([])
            try:
                data = pd.read_csv(csvFile,sep='\t')
                expected_columns = [
                    'Empresa', 'Tipo', 'Cód. de Negociação', 
                    'Cod.ISIN', 'Preço (R$)*','Qtde.', 
                    'Fator Cotação', 'Valor (R$)'
                ]
                
                tickerRegex = '^[\dA-Z]{4}([345678]|11|12|13)$'
                if all(data.columns == expected_columns) \
                    and data['Qtde.'].dtype == np.dtype('int64') \
                    and all(data['Cód. de Negociação'].str.contains(
                        tickerRegex, regex=True)):
                            data = data[['Cód. de Negociação', 'Qtde.']]
                            data.columns = ['Ticker', 'Quantidade']
                            data['Quantidade'] = data['Quantidade'].astype(int) 
                            df = data
                else:
                    raise Exception('Unexpected data')
            except Exception as e:
                pass
            return df

        df = processCSV(self.cleaned_data['file'])
        if df.empty:
            self.add_error(
                'file',
                'Conteúdo do arquivo não possui a formatação esperada'
            )
        return df

class WalletPlanningForm(forms.Form):
    ticker = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='stock-autocomplete',
            attrs={
                #'data-language': 'pt',
                'class':'form-control p-0 m-0 border border-grey',
                'data-minimum-input-length': 3
            }
        )
    )
    quantity = forms.FloatField(
        required=True, label='Quantidade',
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class':'form-control form-control-sm border border-grey',
                'step': '1'
            }
        )
    )

    percent = forms.FloatField(
        label='Porcentagem',
        required=True, 
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class':'form-control form-control-sm border border-grey',
                'step': '0.01'
            }
        )
    )
    
    def clean_ticker(self):
        ticker = self.cleaned_data['ticker']
        try:
            ticker = Stock.objects.get(ticker=ticker)
        except Exception as e:
            raise e
            self.add_error(
                'ticker',
                f'Ticker inválido: {ticker}'
            )
        return ticker

class CapitalForm(forms.Form):
    capital = forms.FloatField(
        label='Aporte', 
        required=True,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                'class':'form-control border border-grey'
            }
        )
    )
    def clean_capital(self):
        capital = self.cleaned_data['capital']
        return round(capital, 2)

class WalletPlanningFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
             return 
        percentTotal = 0
        for form in self.forms:
            percentTotal += form.cleaned_data.get('percent')
        if round(percentTotal,2) != 100:
            self.forms[0].add_error(
                'percent',
                f'Porcentagens não somam 100%. Soma calculada : {percentTotal:.2f}%'
            )

def createWalletPlanningForm(df=None):
    WalletFormSet = formset_factory(
        WalletPlanningForm,
        formset=WalletPlanningFormSet, extra=0, 
        min_num=1, validate_min=True
    )  
    formset = WalletFormSet
    if df is not None:
        nTickers = df.shape[0]
        percent = round(100 / nTickers, 2)
        initialData = [{ 
                'ticker': df['Ticker'].iloc[i],
                'quantity': df['Quantidade'].iloc[i],
                'percent':percent
            } \
            for i in range(nTickers)
        ]
        formset = WalletFormSet(initial=initialData)
    return formset