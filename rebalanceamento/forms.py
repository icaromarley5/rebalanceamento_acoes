from django import forms
from django.utils.safestring import mark_safe

class CEIForm(forms.Form):
    cpf = forms.CharField(
        label='', 
        required=True, 
        max_length=100, 
        widget=forms.TextInput(
            attrs={'placeholder': 'CPF'}))
    password = forms.CharField(
        label='', 
        required=True,
        max_length=100,
        widget=forms.PasswordInput(
            attrs={'placeholder':'Senha'}))
    accept = forms.BooleanField(
        label='', 
        required=False,
        help_text='Permito acesso ao CEI',
        initial=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
    
    def clean_accept(self):
        accept = self.cleaned_data['accept']
        if not accept:
            self.add_error(
                'accept', 
                'Confirme a permissão de acesso.')
        return accept   
 
def createWalletForm(data):
    def clean(self):
        cleanedData = super(type(self), self).clean()
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
        
        for i in range(self.nTickers):
            i = str(i)
            if self.cleaned_data['price' + i] <= 0:
                self.add_error(
                    'price' + i,
                    'Preço precisa ser maior que zero')
    
        return self.cleaned_data
    
    def __init__(self, *args, **kwargs):
            super(type(self),self).__init__(
                *args, 
                **kwargs)
            self.label_suffix = ''
    nTickers = len(data['Ticker'])
    data_dict = {
      'clean': clean,
      'nTickers': nTickers,
      '__init__': __init__,
    }
    percent = round(100 / nTickers, 2)
    
    for i,row in enumerate(list(zip(*data.values()))):
        i = str(i)
        data_dict['ticker' + i] = forms.CharField(
                required=True, initial=row[0],
                widget=forms.HiddenInput())
        data_dict['quantity' + i] = forms.FloatField(
                required=True, initial=row[1],
                widget=forms.HiddenInput())
        data_dict['price' + i] = forms.FloatField(
                required=True, initial=row[2],
                widget=forms.HiddenInput())
        data_dict['percent' + i] = forms.FloatField(
            label=mark_safe(row[0]),
            required=True, initial=percent, 
            widget=forms.NumberInput(
                attrs={'step': '0.01'}))
    data_dict['capital'] = forms.FloatField(
        label=mark_safe('Aporte'), 
        required=True)
    return type('WalletClass', (forms.Form,), data_dict)