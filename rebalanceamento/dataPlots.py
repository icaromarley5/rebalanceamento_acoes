'''
Functions for plotting data
'''

from bokeh.plotting import figure, output_file, show 
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.transform import factor_cmap, dodge
from bokeh.palettes import Spectral6
from bokeh.transform import cumsum
from math import pi

import pandas as pd 

def createPlots(data):
    plan = data['plan']
    nonAllocatedCapital = data['nonAllocatedCapital']

    # bar plot with capital before and after planning
    capital = (plan['Quantidade para comprar'] * plan['Preço']).sum()
    width = 600
    height = 450
    title = 'Planejamento da carteira de ativos'
    tickers = plan['Ticker'].values
    
    source = ColumnDataSource(data=plan)
    p = figure(
        x_range=tickers, 
        title=title,
        y_axis_label='% alocada', 
        plot_width=width,
        plot_height=height,
        )

    p.vbar(
        x=dodge(
            'Ticker', 
            -0.25, 
            range=p.x_range), 
        top='% atual', width=0.2, source=source,
        color="#006666", legend_label="% atual")

    p.vbar(x=dodge(
            'Ticker',  
            0.0,  
            range=p.x_range), 
        top='% planejada', width=0.2, source=source,
        color='#4d4dff', legend_label="% planejada")

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.toolbar.logo = None
    p.toolbar_location = None
    walletScript, walletDiv = components(p)
    
    #pie chart with capital allocation
    x = {
        'Alocado': capital,
        'Não alocado': round(nonAllocatedCapital, 2)}               
                    
    data = pd.Series(x).reset_index(
        name='value').rename(
            columns={'index': 'capital'})
    data['angle'] = data['value'] / data['value'].sum() \
        * 2 * pi
    data['color'] = pd.Series(['#084594', '#9ecae1'])

    p = figure(
        plot_width=width,
        plot_height=height, 
        title="Alocação de capital (%)", 
        toolbar_location=None, tools="hover", 
        tooltips="@capital: @value", 
        x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', 
            include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", 
            fill_color='color', 
            legend_field='capital', 
            source=data)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None
    p.toolbar_location = None
    allocationScript, allocationDiv = components(p)
    
    #bar plot balancing factor
    distance = plan['distance'].abs().sum()
    distancePlanned = plan['distancePlanned'].abs().sum()
    data = {
        'index': [''],
        'Atual': [distance],
        'Planejada': [distancePlanned],
    }
    title = 'Fator de desbalanceamento'
    index = ['']
    
    source = ColumnDataSource(data=data)
    p = figure(
        plot_width=width,
        plot_height=height, 
        x_range=index, 
        title=title,
        )

    p.vbar(x=dodge('index', -0.25, range=p.x_range),
            top='Atual', width=0.2, source=source,
            color="#006666", legend_label="Atual")

    p.vbar(x=dodge('index',  0.0,  range=p.x_range), 
            top='Planejada', width=0.2, source=source,
            color='#4d4dff', legend_label="Planejada")

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.toolbar.logo = None
    p.toolbar_location = None
    factorScript, factorDiv = components(p)

    #bar plot VPA
    distance = (plan['Quantidade'] * plan['VPA']).sum()
    distancePlanned = ((plan['Quantidade'] + plan['Quantidade para comprar']) * plan['VPA']).sum()
    data = {
        'index': [''],
        'Atual': [distance],
        'Planejada': [distancePlanned],
    }
    title = 'Patrimônio (VPA) total'
    index = ['']
    
    source = ColumnDataSource(data=data)
    p = figure(
        plot_width=width,
        plot_height=height, 
        x_range=index, 
        title=title,
        )

    p.vbar(x=dodge('index', -0.25, range=p.x_range),
            top='Atual', width=0.2, source=source,
            color="#006666", legend_label="Atual")

    p.vbar(x=dodge('index',  0.0,  range=p.x_range), 
            top='Planejada', width=0.2, source=source,
            color='#4d4dff', legend_label="Planejada")

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.toolbar.logo = None
    p.toolbar_location = None
    VPAScript, VPADiv = components(p)

    toBuyCol = 'Quantidade para comprar'
    plan[toBuyCol] = plan[toBuyCol].astype(int)
    columns = ['Ticker',toBuyCol,'Preço']
    tickerList = plan[plan[toBuyCol] > 0][columns].values
    
    return {
            'walletScript' : walletScript ,
            'walletDiv' : walletDiv,
            'factorScript': factorScript,
            'VPADiv':VPADiv,
            'VPAScript': VPAScript,
            'factorDiv':factorDiv,
            'allocationScript':allocationScript,
            'allocationDiv':allocationDiv,
            'tickerList':tickerList,
        }