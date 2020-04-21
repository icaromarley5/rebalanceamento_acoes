"""
Functions for creating a investing plan

"""

def computePlan(planDf,capital):
    """
    Rebalacing and investing
    Does rebalancing using a greedy approach
    That minimizes the distance between the planned and actual percentage
    """
    df = planDf.copy()

    waitFor = None
    df['QuantidadeParaComprar'] = 0
    nonAllocatedCapital = capital
    
    df['Valor'] = df['Preço'] * df['Quantidade']
    df['PorcentagemAtual'] = df['Valor'] * 100 / df['Valor'].sum()
    df['distance'] = df['PorcentagemAlvo'] - df['PorcentagemAtual']
    
    df.sort_values(['distance','Preço'], 
                   ascending=False, 
                   inplace=True)
    
    for _,row in df.iterrows():
        targetValue = \
            round((
                df['Valor'].sum() + capital) 
                * row['PorcentagemAlvo'] / 100,
                    2)

        if row['Valor'] < targetValue:   
            valueToAdd = targetValue - row['Valor']
            quant = valueToAdd // row['Preço'] 
            if row['Preço'] > nonAllocatedCapital \
                    or nonAllocatedCapital < valueToAdd:
                # rebalancing not possible
                # buy as much as possible
                waitFor = row['Ticker'] 
                quant = nonAllocatedCapital // row['Preço']        
            nonAllocatedCapital -= row['Preço'] * quant
            df.loc[row.name,'QuantidadeParaComprar'] += quant
        if waitFor:          
            break
    if not waitFor:
        # rebalancing done without problems
        # invest the remaining capital
        df['ValorPlanejado'] = (df['Quantidade'] + df['QuantidadeParaComprar'])\
            * df['Preço']\
            + df['PorcentagemAlvo'] * nonAllocatedCapital
        df['PorcentagemPlanejada'] = df['ValorPlanejado'] * 100 \
            / df['ValorPlanejado'].sum()
        df['distancePlanned'] = df['PorcentagemAlvo'] - df['PorcentagemPlanejada']
        df.sort_values(['distancePlanned', 'Preço'],
                       ascending=False, inplace=True)
        
        for _,row in df.iterrows():
            distanceNow = abs(row['PorcentagemAlvo'] - row['PorcentagemPlanejada'])
            
            quant = 0
            while True:
                quant += 1
                percent = (row['ValorPlanejado'] + quant * row['Preço']) * 100\
                    /df['ValorPlanejado'].sum()
                distanceBuyMore = abs(row['PorcentagemAlvo'] - percent)
                if distanceBuyMore <= distanceNow:
                    if row['Preço'] * quant <= nonAllocatedCapital:
                         continue
                    else:
                        # not enough capital
                        quant -= 1
                        waitFor = row['Ticker']
                        break
                else:
                    # distance can't be minimized
                    quant -= 1
                    break
            if quant == 0 and row['Preço']  <= nonAllocatedCapital: 
                # buy at least one
                quant = 1
            nonAllocatedCapital -= row['Preço'] * quant
            df.loc[row.name,'QuantidadeParaComprar'] += quant
            if waitFor:
                break
    
    df['ValorPlanejado'] = (
        df['Quantidade'] + df['QuantidadeParaComprar']) \
        * df['Preço']
    df['PorcentagemPlanejada'] = df['ValorPlanejado'] * 100 \
        / df['ValorPlanejado'].sum()
    df['distancePlanned'] = df['PorcentagemAlvo'] \
        - df['PorcentagemPlanejada']

    return df, nonAllocatedCapital