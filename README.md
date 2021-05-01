# CarteiraManager V1.0
Gerenciador de Carteiras de ações, com cálculo de IRPF (mensal e Day-Trade) e indicadores via investpy.py
Roda em Python 3.8.
Utiliza os dados do portal Investing.com, através do pacote investpy.

<pre>1) Banco de dados de ativos;</pre>
<pre>2) Posição atual da carteira graficamente;</pre>
<pre>3) Comparação de resultados, normalizados, dos papéis, carteira e IBOV;</pre>
<pre>4) Cálculo do IRPF funciona para ativos que tenham as mesmas regras de ações (derivativos, ETFs, ações);</pre>


Este programa se propõe a gerenciar a carteira de ativos de um investidor.

Qualquer ativo que seguir as regras de imposto de renda de ações e ETFs pode ser gerenciado.

Para começar a usar, basta inserir os valores pedidos no menu "Controles" ou importar um 
arquivo csv (separador ;), em formatação ANSI (obrigatoriamente). As colunas necessárias são dadas a seguir:
Mercado;Papel;Status;Data;Valor;Quantidade;Custos

Em que:
<pre><b>Mercado</b> --> <b>Vista</b> ou <b>Opções</b></pre>
<pre><b>Papel</b> --> Ticker do ativo</pre>
<pre><b>Status</b> --> <b>Compra</b> ou <b>Venda</b></pre>
<pre><b>Data</b> --> Data da Operação, no formato <b>DD/MM/YYYY</b></pre>
<pre><b>Valor</b> --> Valor negociado pelo ativo (compra ou venda). Não use separador de milhar. O separador decimal pode ser a vírgula ou o ponto</pre>
<pre><b>Quantidade</b> --> Quantidade negociada</pre>
<pre><b>Custos</b> --> Taxa da corretora, emolumentos da B3, etc</pre>

Você pode inserir uma entrada a qualquer momento. Os valores de preço médio, 
quantidade consolidada, posição consolidada, serão recalculados automaticamente.

Para editar uma entrada, selecione a mesma da lista, em seguida delete-a, modifique no campo controle o 
que quiser modificar, insira a entrada novamente.

Para o cálculo do IRPF, insira uma data no campo controles (pode ser apenas mês e ano),
no formato DD/MM/AAAA ou MM/AAAA. O imposto será calculado no campo IRPF Mensal, para o mês escolhido.
Na declaração de IRPF anual, no programa de IRPF, caso as vendas do mês ultrapassarem R$20.000,00 (for necessário gerar DARF), lancar em renda variável o valor do (Lucro Bruto - Despesas) para aquele mês.
As informações anuais do IRPF também são computados cumulativamente até o mês informado. Se quiser visualizar os dados computados para o ano inteiro, passe o mês 12 de um referido ano em formato DD/MM/YYYY ou MM/YYYY.
Na declaração de ajuste anual do IRPF, rode o cálculo do IRPF para o mês 12 do Ano Calendário (ano anterior ao ano de exercício do IR). Lance o valor contido em "L. Líquido Vendas Mensais < 20k" em "Rendimentos Isentos e Não Tributáveis, opção 20.")


Se você quiser visualizar os indicadores de um ativo que não possuir em sua carteira,
basta digital o ticker do mesmmo no campo Ação e clicar em Buscar. 
Você também pode selecionar da lista de operações realizadas um ativo de interesse. 
A fonte dos dados é o investpy.

Observações: 

1) Os gráficos "Posição Consolidada" e "Desempenho" podem demorar um pouco para serem atualizados
pois os dados das cotações atuais são puxados da Internet, através do módulo "investpy.py"

2) O gráfico "Desempenho" apresenta os ganhos (ou perdas) normalizados para a primeira operação daquele 
ativo / índice presente em sua carteira. A toda nova operação, o gráfico se renormaliza de acordo.
Assim, um valor de 1 significa que o valor atual é o mesmo investido.
Um valor maior que um, siginifica ganho; um valor menor que um, significa perda.
