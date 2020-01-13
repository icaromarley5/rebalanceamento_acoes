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
2. Executar o script em uma IDE que suporta o console IPython (Spyder, por exemplo). A execução inteira demora pouco menos que um minuto.


## Saída esperada
* Recomendações de ativos para comprar

![Imagem das recomendações](imgs/recomendacao.JPG)

* Gráfico de balanceamento de ativos na carteira: mostra o balanceamento antes e depois do planejamento

![Imagem do balanceamento de ativos da carteira](imgs/carteira.JPG)

* Gráfico de fator de desbalanceamento: compara um índice de desbalanceamento (soma das diferenças da % atual do ativo na carteira e a % alvo) antes e depois do planejamento

![Imagem do fator de desbalanceamento](imgs/fator.JPG)

* Gráfico de alocação de capital: mostra qual percentual do aporte foi alocado

![Imagem da alocação do aporte](imgs/alocacao.JPG)
