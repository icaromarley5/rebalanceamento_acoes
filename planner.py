# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 21:10:48 2020

@author: icaromarley5
"""
import matplotlib.pyplot as plt
#import seaborn as sns
import pandas as pd
from crawlers import get_cei_data, get_tickets_price
import warnings
warnings.filterwarnings("ignore")

def generate_plan(cpf, password, capital):
    print('AVISO: carregando dados da internet, aguarde...')
    
    df = pd.DataFrame(get_cei_data(cpf,password))
    
    df['Preço'] = get_tickets_price(df['Ticket'].values)
    df['Valor'] = df['Preço'] * df['Quantidade']
    df['% atual'] = df['Valor'] * 100 / df['Valor'].sum()
    df['% alvo'] = 100 / df.shape[0]
    print('AVISO: dados carregados com sucesso.'\
          ' Computando planejamento, aguarde...')
    # rebalanceamento e investimentos
    # abordaem gulosa, diminuindo as maiores distâncias
    wait_for = None
    df['Quantidade para comprar'] = 0
    non_allocated_capital = capital
    df['distance'] = df['% alvo'] - df['% atual']
    distance_total_now = df['distance'].abs().sum()
    df.sort_values(['distance','Preço'], ascending=False, inplace=True)
    
    for _,row in df.iterrows():
        target_value = \
            round((df['Valor'].sum() + capital) * row['% alvo'] / 100, 2)
        
        if row['Valor'] < target_value:
            # se aproxime do valor alvo
            quant = (target_value - row['Valor']) // row['Preço'] 
            
            if non_allocated_capital < target_value - row['Valor']:
                # balanceamento não é possível
                # comprar o máximo que for possível
                wait_for = row['Ticket'] 
                quant = non_allocated_capital // row['Preço']
                
        non_allocated_capital -= row['Preço'] * quant
        df.loc[row.name,'Quantidade para comprar'] += quant
        if wait_for:            
            break

    if wait_for:
        print('AVISO: aporte não é suficiente para rebalancear a carteira.\n')
    if not wait_for:
        print('Rebalanceamento concluído com sucesso.'\
              ' Investindo o restante do aporte.')
        # carteira rebalanceada
        # investir dinheiro restante 
        # tenta encaixar capital restante com o rebalanceamento em mente
        # tenta comprar pelo menos um 1 ativo
        df['Valor planejado'] = (df['Quantidade'] + df['Quantidade para comprar'])\
            * df['Preço']\
            + non_allocated_capital
        df['% planejada'] = df['Valor planejado'] * 100 / df['Valor planejado'].sum()
        df['distance_planned'] = df['% alvo'] - df['% planejada']
        df.sort_values(['distance_planned', 'Preço'], ascending=False, inplace=True)
        
        for _,row in df.iterrows():
            distance_now = abs(row['% alvo'] - row['% planejada'])
            
            # tenta encontrar uma quantidade de ações para comprar que reduz a distância
            quant = 0
            while True:
                quant += 1
                percent = (row['Valor planejado'] + quant * row['Preço']) * 100\
                    /df['Valor planejado'].sum()
                distance_buy_more = abs(row['% alvo'] - percent)
                if distance_buy_more <= distance_now:
                    if row['Preço'] * quant <= non_allocated_capital:
                         continue
                    else:
                        # não há capital suficiente
                        quant -= 1
                        wait_for = row['Ticket']
                        break
                else:
                    # distância não pode ser diminuídal
                    quant -= 1
                    break
            if quant == 0 and row['Preço']  <= non_allocated_capital: 
                # tentar comprar pelo menos 1
                quant = 1
            non_allocated_capital -= row['Preço'] * quant
            df.loc[row.name,'Quantidade para comprar'] += quant
            if wait_for:
                break
    
    print('Planejamento concluído com sucesso:')
    print('\nRECOMENDAÇÃO: ações p/ comprar por Ticket:\n')
    for _,row in df[df['Quantidade para comprar'] > 0].iterrows():
        print('\t{}: {:.0f} X R$ {:.2f}'.format(
                row['Ticket'], row['Quantidade para comprar'], 
                row['Preço'])) 
    
    if wait_for:
        print('\nRECOMENDAÇÃO: juntar capital para comprar', wait_for) 
        
    # Plot de balanceamento    
    df['Valor planejado'] = (df['Quantidade'] + df['Quantidade para comprar'])\
        * df['Preço']
    df['% planejada'] = df['Valor planejado'] * 100 / df['Valor planejado'].sum()
    df['distance_planned'] = df['% alvo'] - df['% planejada']
    distance_total_balanced = df['distance_planned'].abs().sum()
    
    ax = df.set_index('Ticket').sort_index()[['% atual', '% planejada']]\
        .plot(kind='bar', figsize=(9, 5), stacked=False)
    plt.title('Carteira balanceada')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.95))
    plt.show()
    
    pd.DataFrame({
                'Atual': [distance_total_now],
                'Planejada': [distance_total_balanced],
    }).plot(kind='bar')
    plt.xticks([])
    plt.title('Fator de desbalanceamento (%)')
    plt.show()
        
    # Plot de alocação de capital
    allocated_capital =  capital - non_allocated_capital
    df_aux = pd.DataFrame({'Valores': [non_allocated_capital,allocated_capital]},
                           index=['Não alocado', 'Alocado'])
    ax = df_aux.plot(kind='pie',
            y='Valores',labels=None, autopct=lambda p: '{:.2f}%'.format(p))
    ax.set_ylabel('')
    plt.title('Capital não alocado: R$ {:.2f}'.format(non_allocated_capital))   
    plt.show()