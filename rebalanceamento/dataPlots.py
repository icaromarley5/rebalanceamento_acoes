'''
Functions for plotting data
'''

import pandas as pd 
import numpy as np 

import plotly.express as px

currentColor = '#104578'
plannedColor = '#196ebf'
targetColor = '#309bff'

def to_html(fig):
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        include_mathjax=False,
        config={'responsive': True}
    )

def createPlots(data):
    plan = data['plan']
    nonAllocatedCapital = data['nonAllocatedCapital']
    allocatedCapital = data['allocatedCapital']

    # ticker list
    toBuyCol = 'QuantidadeParaComprar'
    plan[toBuyCol] = plan[toBuyCol].astype(int)
    columns = ['Ticker', toBuyCol, 'Preço']
    tickerList = plan[plan[toBuyCol] > 0][columns].values

    return {  
        'figList':[
            plotWalletAllocation(
                allocatedCapital, nonAllocatedCapital
            ), 
            plotFactor(plan),
            plotWallet(plan),
            plotVPA(plan),

        ],
        'tickerList': tickerList,
    }

def plotWalletAllocation(
    allocatedCapital, nonAllocatedCapital):
        data = {
            'Valor': [allocatedCapital, nonAllocatedCapital],
            'Alocação': ['Alocado', 'Não alocado'],
        }
        fig = px.pie(
            data, values='Valor', names='Alocação', 
            title='Alocação de capital (%)',
            color_discrete_sequence=['#003866', '#3778ad']
        )
        fig.update_traces(
            hoverinfo='value', textinfo='percent',
            hovertemplate='R$ %{value:.2f}', 
            texttemplate='%{percent}'
        )
        fig.update_layout(separators = ',')
        return to_html(fig)

def plotFactor(plan):
    #bar plot balancing factor
    distance = plan['distance'].abs().sum()
    distancePlanned = plan['distancePlanned'].abs().sum()
    data = {
        'Valor': [distance, distancePlanned],
        'Carteira': ['Atual', 'Planejada'],
    }
    colorSeq = [
        currentColor, plannedColor
    ]
    fig = px.bar(
        data, y='Valor', x='Carteira', color='Carteira', 
        title='Fator de desequilíbrio (%)',
        color_discrete_sequence=colorSeq,
    )
    fig.update_layout(
        separators = ',',
        plot_bgcolor='white',
    )
    fig.update_yaxes(
        showgrid=False, title=''
    )
    fig.update_xaxes(
        showticklabels=False,
        title = "",
    )
    fig.update_traces(
        hovertemplate='%{y:.2f}%<extra></extra>',
    )
    return to_html(fig)
                
def plotVPA(plan):
    VPA = (plan['Quantidade'] * plan['VPA']).sum()

    totalQuant = \
        plan['Quantidade'] \
        + plan['QuantidadeParaComprar']
    VPAPlanned = (
        totalQuant \
        * plan['VPA']
    ).sum()
    data = {
        'Valor': [VPA,VPAPlanned],
        'Carteira': ['Atual','Planejada'],
    }
    
    colorSeq = [currentColor, plannedColor]
    fig = px.bar(
        data,
        y='Valor',
        x='Carteira',
        color='Carteira',
        title='Patrimônio acionário',
        color_discrete_sequence=colorSeq
    )
    fig.update_layout(
        separators = ',',
        plot_bgcolor='white',
    )
    fig.update_yaxes(
        showgrid=False, 
        title=''
    )
    fig.update_xaxes(
        showticklabels=False,
        title = "",
    )
    fig.update_traces(
        hovertemplate='R$ %{y:.2f}<extra></extra>',
    )
    return to_html(fig)

def plotWallet(plan):
    columns = [
        'Ticker','PorcentagemAtual',
        'PorcentagemPlanejada',
        'PorcentagemAlvo'
    ]
    data = plan[columns].copy()
    data.columns = ['Ticker', 'Atual', 'Planejada', 'Alvo']  
    data = data.melt(
        'Ticker',
        value_vars=[
            'Atual', 'Planejada', 'Alvo'
        ],
        var_name='Carteira',
        value_name='Porcentagem'
    )

    colorSeq = [
        currentColor,
        plannedColor, 
        targetColor
    ]
    fig = px.bar(
        data,
        y='Porcentagem',
        x='Ticker',
        color='Carteira',
        title='Composição da carteira (%)',
        barmode='group',
        color_discrete_sequence=colorSeq)
    fig.update_layout(
        separators = ',',
        plot_bgcolor='white',
    )
    fig.update_yaxes(
        showgrid=False,
        title = "",
    )
    fig.update_xaxes(
        title = "",
        tickangle=90,
    )
    fig.update_traces(
        hovertemplate='%{y:.2f}%<extra></extra>',
    )
    return to_html(fig)