# rebalanceamento_acoes
Script para fazer o rebalanceamento e investimento através de um aporte em uma carteira de ações focada no Buy and Hold.

## Rebalanceamento

O rebalanceamento prioriza:
1. o maior atraso em relação à porcentagem automaticamente definida (100/número de ações), aplicada sobre o total da carteira (desconsiderando aporte) 
2. maior cotação

Para cada ativo, o script tenta atingir essa porcentagem (caso esteja atrasado) ou pelo menos comprar 1 ativo.

## Investimento

O investimento é feito com o restante do aporte, após um rebalanceamento que concluído com sucesso (compra de todos os ativos atrasados).
Nele, apenas a maior cotação é utilizada como meio de ordenação e a porcentagem é aplicada apenas no restante do aporte.
Similar ao rebalanceamento, o objetivo é comprar pelo menos 1 ação de cada ativo.

## Instruções
1. Editar o arquivo main.py com o valor do aporte (capital), cpf (cpf), senha do CEI (password) e código da corretora (cod) disponíveis nas linhas 16-20
2. Executar o script em uma IDE que suporta IPython (Spyder, por exemplo) 
