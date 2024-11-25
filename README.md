
# Projeto Previsão de Vendas Rossmann


![Rossmann Store](/img/rossmann_store.png)


## Problema de Negócio
Os gerentes da Rossmann enfrentam o desafio de prever com precisão as vendas diárias com até seis semanas de antecedência, influenciadas por fatores como promoções, concorrência, feriados escolares e estaduais, sazonalidade e características locais. A realização de previsões independentes e heterogêneas resulta em falta de uniformidade e confiabilidade, comprometendo decisões estratégicas.

## Objetivo
Desenvolver uma solução automatizada baseada em Machine Learning para prever vendas diárias com até seis semanas de antecedência de maneira precisa e confiável. A aplicação será acessível remotamente e oferecerá aos gerentes uma ferramenta prática e eficiente para otimizar o planejamento de estoques, alocação de recursos e campanhas promocionais, garantindo resultados mais consistentes.

## Produto Final
O resultado é um bot no Telegram que, ao receber o número de uma loja, gera previsões para as próximas seis semanas, acompanhadas de gráficos que destacam os dias de maior relevância semanal nas vendas, proporcionando suporte estratégico ágil e visualmente claro.
 
![bot](/img/bot_telegram.png)
## [Link para o Bot](https://t.me/TheRossmannBot)
## Grafico para auxilio na tomada de decisão
![graph_final](/img/graph_final.png)

#
# Planejamento da solução
Utilizei o método **CRISP-DM** para estruturar desde o entendimento do problema de negócio e análise dos dados até a modelagem e avaliação dos resultados. A seguir, demonstro os passos do desenvolvimento, os principais insights e os resultados obtidos ao longo da primeira interação completa.

![crisp](/img/crisp.png)

#### 1. Compreensão do negócio
- Definição do problema a ser solucionado e estabelecimento dos objetivos do projeto.

#### 2. Compreensão dos dados
- Coleta e análise inicial dos dados para identificar problemas e possibilidades de resolução.
- Análise exploratória dos dados para geração de insights e identificação de inconsistências.

#### 3. Preparação dos dados
- Limpeza de Dados: Remoção de dados inconsistentes e preenchimento de valores ausentes.
- Data Engeneering: Criação de novas variáveis a partir dos dados brutos.
- Transformação dos dados: Conversão dos dados para o formato adequado para modelagem.

#### 4. Modelagem
- Seleção e aplicação dos algoritmos de machine learning.
- Encontrar a melhor combinação de parâmetros para controle de overfit e underfit dos modelos.
- Aplicação da técnica de **Cross-Validation** para garantir resultados confiáveis.

#### 5. Avaliação
- Avaliação do desempenho do modelo com base em métricas específicas (MAE, MAPE, RMSE).
- Análise dos resultados para garantir que o modelo atenda aos objetivos do negócio.
- Análise de viabilidade para encontrar a melhor relação entre tamanho/custo dos modelos e seus resultados.

#### 6. Implantação do modelo em um ambiente de produção.
- Implantação do Modelo: Disponibilização do modelo em uma API que recebe novos dados e retorna previsões.
- Bot no Telegram: Desenvolvimento de um bot para facilitar o acesso e interação do usuário com o modelo.

#

# Principais Insigths

#### 1- Lojas com sortimento extra tem uma média de venda maior, mas tem uma menor quantidade de lojas e vendas se comparadas com o tipo basic e extended.
![sales_assortment](/img/sales_assortment.png)

#### 2- Lojas com competidores a pouco tempo tendem a ter menos vendas mas aquelas com competidores a mais de 150 meses vendem mais.
![competition_time](/img/competition_time.png)

#### 3- Houve uma redução na quantidade de vendas ao decorrer do tempo, porém o ano de 2015 ainda está em andamento.
![sales_month](/img/sales_month.png)


# 
# Machine Learning

## Modelos utilizados e resultados 
![models result](/img/models_performance.png)

#### 1. Random Forest Regressor  
- Demonstrou um ótimo desempenho com o menor erro em todas métricas.

#### 2. XGBoost  
- Demonstrou ótimo desempenho e equilíbrio entre precisão e eficiência computacional.

#### 3. Average Model  
- Modelo padrão utilizado como baseline, baseado na média das vendas históricas.  
- Auxiliou na medição da melhoria alcançada pelos modelos mais complexos.

#### 4. Linear Regression  
- Modelo linear aplicado para verificar se os dados apresentavam comportamento linear.  
- Serviu como um ponto de referência inicial, mas obteve desempenho inferior aos modelos mais avançados.

#### 5. Linear Regression - Lasso  
- Variante regularizada da regressão linear, utilizada para avaliar se variáveis menos relevantes poderiam ser eliminadas sem perda significativa de desempenho.  
- Confirmou que os dados não seguiam um padrão linear evidente. 


## Métricas de Avaliação

#### 1. MAE (Mean Absolute Error)  
- Mede o erro absoluto médio entre valores reais e previstos.  

#### 2. MAPE (Mean Absolute Percentage Error)  
- Expressa o erro em porcentagem, permitindo uma visão voltada ao negócio do resultado.  

#### 3. RMSE (Root Mean Squared Error)  
- Penaliza grandes erros por calcular a raiz do erro médio ao quadrado. 


## Cross Validation no Projeto

 Utilizei Cross Validation para avaliar a performance do modelo, levando em consideração a natureza temporal dos dados. Como o objetivo era prever as vendas diárias e semanais, com variações ao longo do tempo, era fundamental validar o modelo de forma que refletisse essas mudanças.

### Como foi aplicada:

- Ao invés de realizar uma divisão aleatória dos dados, apliquei uma **divisão temporal**, onde os dados foram separados em períodos consecutivos.
- O modelo foi treinado com dados de um período e validado com dados de períodos posteriores. Isso garantiu que a previsão fosse robusta e capaz de generalizar bem para dados futuros, considerando as variações sazonais.

A imagem abaixo ilustra o processo de **Cross Validation** aplicado nos dados.

![models result](/img/cross_val.png)
## Resultados
![models result](/img/model_cross_validation.png)

+/- representa o desvio padrão dos resultados em relação ao valor inicial.

## Escolha do Modelo Final

Após utilizar o Average Model como base e avaliar os modelos lineares, o **Random Forest** foi testado e apresentou bons resultados. No entanto, o **XGBoost** foi escolhido como modelo final devido à sua **eficiência computacional** e **menor uso de memória**, fatores essenciais para a execução em um servidor gratuito. Embora o **Random Forest** tenha apresentado desempenho satisfatório, o **XGBoost** se destacou pela **escalabilidade** e **robustez**, oferecendo uma solução mais leve e rápida, ideal para o projeto, especialmente em um ambiente com recursos limitados.



