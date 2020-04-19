from django import forms
from django.utils.safestring import mark_safe

from django.core.validators import FileExtensionValidator

import pandas as pd 
from rebalanceamento import tickerData

class WalletDataForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(['csv'])], 
        label='Arquivo CSV')
 
    def clean_file(self):
        df = tickerData.processCSV(self.cleaned_data['file'])
        if df.empty:
            self.add_error('file','Conteúdo do arquivo não possui a formatação esperada')
        return df

def createWalletPlanningForm(df):
    def clean(self):
        cleanedData = super(type(self), self).clean()
        if self.is_valid():
            capital = self.cleaned_data['capital']
            if capital <= 0:
                self.add_error(
                    'capital', 
                    'Valor precisa ser acima de zero.')
            self.cleaned_data['capital'] = round(capital, 2) 
            
            total = 0
            for i in range(self.nTickers):
                i = str(i)
                total +=  cleanedData['percent' + i]
            if round(total, 2) != 100:
                self.add_error(
                    'percent0', 
                    'A soma total precisa ser 100.'\
                        'Soma atual: {:.2f}'.format(total))
        return self.cleaned_data
    
    def __init__(self, *args, **kwargs):
            super(type(self),self).__init__(
                *args, 
                **kwargs)
            self.label_suffix = ''
    nTickers = df.shape[0]
    data_dict = {
      'clean': clean,
      'nTickers': nTickers,
      '__init__': __init__,
    }
    percent = round(100 / nTickers, 2)
    
    for i,row in df.iterrows():
        i = str(i)
        data_dict['ticker' + i] = forms.CharField(
                required=True, initial=row['Ticker'],
                widget=forms.HiddenInput())
        data_dict['quantity' + i] = forms.FloatField(
                required=True, initial=row['Quantidade'],
                widget=forms.HiddenInput())
        data_dict['percent' + i] = forms.FloatField(
            label=mark_safe(row['Ticker']),
            required=True, initial=percent, 
            widget=forms.NumberInput(
                attrs={'step': '0.01'}))
    data_dict['capital'] = forms.FloatField(
        label=mark_safe('Aporte'), 
        required=True)
    return type('WalletClass', (forms.Form,), data_dict)

def createWalletPlanningFormPOST(data):
    if (len(data)-2) % 3 == 0:
        nRows = (len(data)-2) // 3
        columns = ['capital']
        columns += ['ticker' + str(i) for i in range(nRows)]
        columns += ['percent' + str(i) for i in range(nRows)]
        columns += ['quantity' + str(i) for i in range(nRows)]
        
        if len(set(list(data.keys()) + columns)) == len(columns) + 1: # same keys
            df = pd.DataFrame([])
            df['Ticker'] = [data['ticker' + str(i)] for i in range(nRows)]
            df['Quantidade'] = [data['quantity' + str(i)] for i in range(nRows)]
            return createWalletPlanningForm(df)
    return None