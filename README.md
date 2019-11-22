# rebalanceamento_acoes
Script para fazer o rebalanceamento de uma carteira de ações focada no Buy and Hold

O rebalanceamento é feito da seguinte forma:
1. Os ativos são ordenados por atraso em relação à porcentagem definida e maior cotação
2. Para cada ativo, são selecionadas n ações (considerando a porcentagem definida)
3. O processo é refeito até naõ ser possível comprar mais com o aporte definido

## Instruções
1. Editar o arquivo wallet.csv com as quantidades, porcentagens e Tickets da sua carteira de ações
2. Colocar o valor do aporte na linha 14 em main.py 
3. Executar o script
