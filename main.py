# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 09:47:31 2019

@author: icaromarley5
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from crawlers import get_cei_data, get_tickets_price
import warnings
warnings.filterwarnings("ignore")

# para preencher
capital = 0 # valor do aporte

cpf = '' # cpf
password = '' # senha cei
cod = ''# código corretora

df = pd.DataFrame(get_cei_data(cpf,password,cod))

df['Preço'] = df['Ticket'].apply(get_tickets_price)
df['Valor'] = df['Preço'] * df['Quantidade']
df['% atual'] = df['Valor']*100/df['Valor'].sum()
df['% alvo'] = 100/df.shape[0]

# rebalanceamento e investimentos
df['Quantidade para comprar'] = 0
non_allocated_capital = capital
wait_for = None
df['distance'] = (df['% alvo'] - df['% atual']).abs()
df.sort_values(['distance','Preço'],ascending=False,inplace=True)
for i,row in df.iterrows():
    # rebalanceamento
    # tenta deixar todos os ativos com o % planejado
    
    target_value = df['Valor'].sum() * row['% alvo']/100
    if row['Valor'] < target_value: 
        # se aporte é suficiente para rebalancear ativos com percentuais maiores
        if row['Preço'] + row['Valor'] <= target_value:
            # compre ate atingir o target value
            quant = (target_value-row['Valor'])//row['Preço']
        else:
            # aporte insuficiente para manter rebalanceamento
            if row['Preço'] < non_allocated_capital:
                # compre pelo menos 1
                quant = 1  
            else:
                # aporte insuficiente para comprar pelo menos uma ação
                wait_for = row['Ticket']
                break            
        non_allocated_capital -= row['Preço'] * quant
        df.loc[row.name,'Quantidade para comprar'] = quant
del df['distance']

# Plot de balanceamento    
df['Valor planejado'] = (df['Quantidade']+df['Quantidade para comprar']) * df['Preço']
df['% planejada'] = df['Valor planejado']*100/df['Valor planejado'].sum()

ax = df.set_index('Ticket').sort_index()[['% atual','% planejada']].plot(kind='bar',figsize=(9,5),stacked=False)
plt.title('Carteira balanceada')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.95))
plt.show()


if wait_for: 
    print('Aporte é insuficiente para rebalancear a carteira')
else:
    print('Rebalanceamento processado com sucesso')
    # rebalanceamento concluído com sucesso
    # tenta alocar o dinheiro restante
    # prioridade: ação com maior preço
    
    new_capital = non_allocated_capital
    df.sort_values('Preço',ascending=False,inplace=True)
    
    for i,row in df.iterrows():
        quant = 0
        target_value = new_capital * row['% alvo']/100
        
        if row['Preço'] > target_value: 
            # não sobrou dinheiro suficiente para comprar o ativo
            # compra pelo menos uma
            if row['Preço'] <= non_allocated_capital:
                quant = 1
            else:
                print('Restante do aporte é insuficiente para comprar ações mais caras')
                wait_for = row['Ticket']
                break
        else:
            # compra ações até a % alvo
            quant = (target_value)//row['Preço']
            
        non_allocated_capital -= row['Preço'] * quant
        df.loc[row.name,'Quantidade para comprar'] += quant
   

# Plot de balanceamento    
df['Valor planejado'] = (df['Quantidade']+df['Quantidade para comprar']) * df['Preço']
df['% planejada'] = df['Valor planejado']*100/df['Valor planejado'].sum()

ax = df.set_index('Ticket').sort_index()[['% atual','% planejada']].plot(kind='bar',figsize=(9,5),stacked=False)
plt.title('Carteira balanceada após investimentos')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.95))
plt.show()

# Plot de alocação de capital
allocated_capital = capital-non_allocated_capital
ax = pd.DataFrame({'Valores':[non_allocated_capital,allocated_capital]},
                  index=['Não alocado','Alocado']).plot(kind='pie',y='Valores',labels=None,
                        autopct=lambda p: '{:.2f}%'.format(p))
ax.set_ylabel('')
plt.title('Capital não alocado: R$ {:.2f}'.format(non_allocated_capital))   
plt.show()

print()
print('Quantidade de ações para comprar com R$ {:.2f} por Ticket:'.format(capital))
for _,row in df[df['Quantidade para comprar']>0].iterrows():
    print('\t{}: {:.0f}'.format(row['Ticket'],row['Quantidade para comprar'])) 
print()
if wait_for:
    print('Recomendação: juntar $ para comprar mais ações de',wait_for)