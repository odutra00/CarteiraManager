# CarteiraManager V1.0
Gerenciador de Carteiras de ações, com cálculo de IRPF (mensal e Day-Trade) e indicadores via investpy.py

1) Banco de dados de ativos;
2) Posição atual da carteira graficamente;
3) Comparação de resultados, normalizados, dos papéis, carteira e IBOV;
4) Cálculo do IRPF funciona para ativos que tenham as mesmas regras de ações (derivativos, ETFs, ações);


Este programa se propõe a gerenciar a carteira de ativos de um investidor.

Qualquer ativo que seguir as regras de imposto de renda de ações e ETFs pode ser gerenciado.

Para começar a usar, basta inserir os valores pedidos no menu "Controles" ou importar um 
arquivo csv, em formatação ANSI (obrigatoriamente). As colunas necessárias são exemplificadas 
no exemplo ExemploCSVImportacao.csv

Você pode inserir uma entrada a qualquer momento. Os valores de preço médio, 
quantidade consolidada, posição consolidada, serão recalculados automaticamente.

Para editar uma entrada, selecione a mesma da lista, em seguida delete-a, modifique no campo controle o 
que quiser modificar, insira a entrada novamente.

Para o cálculo do IRPF, insira uma data no campo controles (pode ser apenas mês e ano),
no formato DD/MM/AAAA ou MM/AAAA. O imposto será calculado no campo IRPF Mensal.

Se você quiser visualizar os indicadores de um ativo que não possuir em sua carteira,
basta digital o ticker do mesmmo no campo Ação e clicar em Buscar.
Você também pode selecionar da lista de entradas um ativo operado no mês de interesse. Daí, é 
só clicar em Calcula IRPF Mensal.

Observações: 

1) Os gráficos "Posição Consolidada" e "Desempenho" podem demorar um pouco para serem atualizados
pois os dados das cotações atuais são puxados da Internet, através do módulo "investpy.py"

2) Os gráficos "Posição Consolidada" e "Desempenho" não são desenhados automaticamente devido 
MatPlotlib não funcionar com threads. Assim, após a barra de loading finalizar, clique em algum controle 
de gráfico e depois no gráfico para que o mesmo seja desenhado.

3) O gráfico "Desempenho" apresenta os ganhos (ou perdas) normalizados para a primeira operação daquele 
ativo / índice presente em sua carteira. A toda nova operação, o gráfico se renormaliza de acordo.
Assim, um valor de 1 significa que o valor atual é o mesmo investido.
Um valor maior que um, siginifica ganho; um valor menor que um, significa perda.