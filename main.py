# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 09:47:31 2019

@author: icaromarley5
"""
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

capital = 100

info_url = 'https://www.fundamentus.com.br/detalhes.php?papel='
df = pd.read_csv('wallet.csv')

def get_data(row):
    r = requests.get(info_url+row['Ticket'])
    return BeautifulSoup(r.text)
df['Dados'] = df.apply(get_data,axis=1)

def get_price(soup):
    return float(soup.find('td',{'class':'data destaque w3'}).span.text.replace(',','.')) 

df['Preço'] = df['Dados'].apply(get_price)
df['Valor'] = df['Preço'] * df['Quantidade']
df['% atual'] = df['Valor']*100/df['Valor'].sum()

def get_vpa(soup):   
    return float(soup.find('span',{'class':'txt'},text='VPA').findNext('td').text.replace(',','.'))
df['Vpa'] = df['Dados'].apply(get_vpa)

del df['Dados']

df['Quantidade para comprar'] = 0
non_allocated_capital = capital
df['% planejada'] = df['% atual']
df['Valor planejado'] = df['Valor']
while True:
    df['bought'] = False
    non_allocated_capital_old = non_allocated_capital
    while True:
        df['distance'] = (df['% alvo'] - df['% planejada']).abs()
        df.sort_values('Preço',ascending=False,inplace=True)
        df.sort_values('distance',ascending=False,inplace=True)
        non_bought = df[df['bought']==False]
        
        if not non_bought.empty:
            row = non_bought.iloc[0]
            
            if row['Preço'] <= non_allocated_capital:
                
                target_value = (df['Valor planejado'].sum() + capital) * row['% alvo']/100
                if target_value > row['Valor planejado']:
                    target_quant = target_value//row['Preço'] - row['Quantidade'] - row['Quantidade para comprar']
    
                    quant = non_allocated_capital//row['Preço']
                                     
                    if quant > target_quant:
                        quant = target_quant
                                            
                    non_allocated_capital -= row['Preço'] * quant
                    df.loc[row.name,'Quantidade para comprar'] += quant

            df.loc[row.name,'bought'] = True 
        else:break
    
    df['Valor planejado'] = (df['Quantidade']+df['Quantidade para comprar']) * df['Preço']
    df['% planejada'] = df['Valor planejado']*100/df['Valor planejado'].sum()

    if non_allocated_capital == non_allocated_capital_old:
        break
del df['bought'],df['distance']

ax = df.set_index('Ticket').sort_index()[['% atual','% planejada','% alvo']].plot(kind='bar',figsize=(9,5))
plt.title('Carteira')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.95))
plt.show()

print('PL atual: R$ {:.2f}'.format((df['Vpa']*df['Quantidade']).sum()))
print('PL planejado: R$ {:.2f}'.format((df['Vpa']*(df['Quantidade']+df['Quantidade para comprar'])).sum()))
print('Capital não alocado: R$ {:.2f}'.format(non_allocated_capital))
print()
print('Quantidade de ações para comprar com R$ {:.2f} por Ticket:'.format(capital))
for _,row in df[df['Quantidade para comprar']>0].iterrows():
    print('\t{}: {:.0f}'.format(row['Ticket'],row['Quantidade para comprar'])) 