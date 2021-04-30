#import About
from Gui import *
from datetime import date
from datetime import timedelta
import Backend as core
from datetime import datetime
import csv
import investpy as inv
from tkinter import messagebox
import pandas as pd
import numpy as np
import threading
from multiprocessing import Process

app = None

def escreveLista(rows):
    for i in app.listPapels.get_children():
        app.listPapels.delete(i)
    novaR = preparaDadosExibicaoLista(rows)
    booleano = TRUE
    for row in novaR:
        if booleano:
            app.listPapels.insert("", "end", text=row[0], values=row[1:], tags="impar")
            booleano = FALSE
        else:
            app.listPapels.insert("", "end", text=row[0], values=row[1:], tags="par")
            booleano = TRUE

def view_command():
    rows = core.viewAll()
    escreveLista(rows)
    if app.entPapel.get():
        getIndicadoresTecnicos(app.entPapel.get())
        getIndicadoresFundamentalistas(app.entPapel.get())

def search_command():
    dataCorreta, data, tipo = getDate()
    if dataCorreta:
        if tipo == 'DiaMesAno':
            rows = core.search(app.txtMercado.get(), app.txtPapel.get(), app.txtStatus.get(),
                               data, '', '', app.txtValorCompra.get(), '',
                               app.txtQuantidade.get(), '', app.txtCustos.get())
        elif tipo == 'MesAno':
            rows = core.searchMonthandYear(app.txtMercado.get(), app.txtPapel.get(), app.txtStatus.get(), '',
                                           data.month,
                                           data.year,
                                           app.txtValorCompra.get(), '', app.txtQuantidade.get(), '',
                                           app.txtCustos.get())
        else:
            rows = core.search(app.txtMercado.get(), app.txtPapel.get(), app.txtStatus.get(), '', '',
                               data.year, app.txtValorCompra.get(), '',
                               app.txtQuantidade.get(), '', app.txtCustos.get())
    else:
        rows = core.search(app.txtMercado.get(), app.txtPapel.get(), app.txtStatus.get(), '', '', '',
                           app.txtValorCompra.get(), '', app.txtQuantidade.get(), '', app.txtCustos.get())

    escreveLista(rows)

    if app.entPapel.get():
        getIndicadoresTecnicos(app.entPapel.get())
        getIndicadoresFundamentalistas(app.entPapel.get())


def preparaDadosExibicaoLista(rows):
    # using pop() + list comprehension
    # deleting column element of row
    novaR = list()
    for r in rows:
        listaNova = list()
        data = r[4].split()
        data1 = data[0].split('-')
        novaData = data1[2] + "/" + data1[1] + "/" + data1[0]
        lista = list(r)
        lista[4] = novaData #substitui a data em formato date para o formato por /s
        lista[7] = "${:,.2f}".format(lista[7])
        lista[8] = "${:,.2f}".format(lista[8])
        lista[11] = "${:,.2f}".format(lista[11])
        del lista[5:7] #remove data em formato date, o mês e o ano
        del lista[0] #remove index
        del lista[9:13]

        for item in lista:
            #item = '\t' + str(item)
            listaNova.append(item)
        novaR.append(listaNova)
    return novaR

def insert_command():#insere o novo papel atualizando as informações no DB que são
                    #calculadas automaticamente (PM, consolidado?, posicaoAtual,
                    #valorAtual, dataFechamento
    dataCorreta, data, tipo = getDate()
    if tipo == 'DiaMesAno':
        # pm, consolidado = calculaPmConsolidado(app.txtMercado.get(),
        #                                     app.txtPapel.get(),
        #                                     app.txtStatus.get(),
        #                                     data,
        #                                     getdouble(app.txtValorCompra.get().replace(',', '.')),
        #                                     int(app.txtQuantidade.get()))
        core.insert(app.txtMercado.get(),
                    app.txtPapel.get(),
                    app.txtStatus.get(),
                    data,
                    data.month,
                    data.year,
                    getdouble(app.txtValorCompra.get().replace(',', '.')),
                    '',
                    int(app.txtQuantidade.get()),
                    '',
                    getdouble(app.txtCustos.get().replace(',', '.')),
                    '',
                    '',
                    '',
                    '')
    updateAll()



#deveriam ter status TRUE para consolidado quando é a última operação daquele papel
def updatePMConsolidado():#atualiza uma entrada do DB. Atualiza os charts
    dataCorreta, data, tipo = getDate()
    operacoesPapel = core.viewAll()
    for operacaoPapel in operacoesPapel:
        #(mercado, papel, status, data, valor , quantidade)
        pm, consolidado = calculaPmConsolidado( operacaoPapel[0],
                                                operacaoPapel[1],
                                                operacaoPapel[2],
                                                operacaoPapel[3],
                                                operacaoPapel[4],
                                                operacaoPapel[7],
                                                operacaoPapel[9])
        core.update(operacaoPapel[0],
                    operacaoPapel[1],
                    operacaoPapel[2],
                    operacaoPapel[3],
                    operacaoPapel[4],
                    datetime.strptime(operacaoPapel[4], "%Y-%m-%d %H:%M:%S").month,
                    datetime.strptime(operacaoPapel[4], "%Y-%m-%d %H:%M:%S").year,
                    operacaoPapel[7],
                    pm,
                    operacaoPapel[9],
                    consolidado,
                    operacaoPapel[11],
                    '',
                    operacaoPapel[13],
                    operacaoPapel[14],
                    operacaoPapel[15])

    operacoesPapel = core.viewAll()
    for operacaoPapel in operacoesPapel:
        core.updateConsolidado(operacaoPapel[0], "FALSE")

    papeis = core.searchPapeisDistintos()
    for papel in papeis:
        operacoesPapel = core.searchPapeisDistintosDataDescendente(papel)
        core.updateConsolidado(operacoesPapel[0][0], "TRUE")


def updateAll():
    updatePMConsolidado()
    updateDayTrade()
    #updateValorAtual()
    view_command()
    #iniciaThreadDesempenho()
    iniciaThreadPie()
    if app.entPapel.get():
        getIndicadoresTecnicos(app.entPapel.get())
        getIndicadoresFundamentalistas(app.entPapel.get())


def del_command():#deleta uma entrada do db. atualiza o pm e os charts
    entrada = selected
    entradaLista = list(entrada)
    i = 0
    for row in entradaLista:
        entradaLista[i] = row.replace("\t", "")
        i = i + 1
    i = 0
    for row in entradaLista:
        entradaLista[i] = row.replace("$", "")
        i = i + 1

    id = core.search2Delete(entradaLista[0],
                            entradaLista[1],
                            entradaLista[2],
                            datetime.strptime(entradaLista[3], "%d/%m/%Y"),
                            entradaLista[4],
                            entradaLista[5],
                            entradaLista[6],
                            entradaLista[7],
                            entradaLista[8])
    core.delete(id[0])
    updateAll()


def getSelectedRow(event):
    global selected
    focused = app.listPapels.focus()
    selected = app.listPapels.item(focused, "values")
    categoria = app.listPapels.item(focused, "text")
    selected = [categoria] + list(selected)

    app.comboMercado.delete(0, END)
    app.comboMercado.insert(END, selected[0].replace('\t', ''))
    app.entPapel.delete(0, END)
    app.entPapel.insert(END, selected[1].replace('\t', ''))
    app.comboStatus.delete(0, END)
    app.comboStatus.insert(END, selected[2].replace('\t', ''))
    app.entData.delete(0, END)
    app.entData.insert(END, selected[3].replace('\t', ''))
    app.entValor.delete(0, END)
    app.entValor.insert(END, selected[4].replace('$', '')) #backend view original indice 7
    app.entQuantidade.delete(0, END)
    app.entQuantidade.insert(END, selected[6].replace('\t', ''))#backend view original indice 9
    app.entCustos.delete(0, END)
    app.entCustos.insert(END, selected[8].replace('$', ''))#backend view original indice 11
    if app.entPapel.get():
        getIndicadoresTecnicos(app.entPapel.get())
        getIndicadoresFundamentalistas(app.entPapel.get())
    return selected


############export csv
def exportCSV():
    filename = filedialog.asksaveasfilename(
                defaultextension='.csv', filetypes=[("csv files", '*.csv')],
                #initialdir=app.default_path_to_pref,
                title="Choose filename")   #askopenfilename(parent=app.window)
    with open(filename, mode='w') as operacoes:
        operacoes_writer = csv.writer(operacoes, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        operacoes_writer.writerow(['Numero da Operação', 'Mercado', 'Papel', 'Status', 'Data', 'Mes', 'Ano', 'Valor',
                                   'PM', 'Quantidade', 'Quantidade Consolidada', 'Custos', 'Consolidado',
                                   'Valor Atual', 'Data de Fechamento', 'Day-Trade'])
        # rows = app.listPapels.get(0, END)
        # for row in rows:
        #     operacoes_writer.writerow(row)
        rows = core.viewAll()
        for row in rows:
            tupleAsList = list(row)
            tupleAsList[4] = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
            rowNew = tuple(tupleAsList)
            operacoes_writer.writerow(rowNew)


##########import CSV file into DB
def importCSV():
    csvFile = openFile()
    csvDict = csv.DictReader(csvFile, delimiter=";")
    for operacao in csvDict:
        core.insert(operacao["Mercado"],
                    operacao["Papel"],
                    operacao["Status"],
                    datetime.strptime(operacao["Data"], '%d/%m/%Y'),
                    datetime.strptime(operacao["Data"], '%d/%m/%Y').month,
                    datetime.strptime(operacao["Data"], '%d/%m/%Y').year,
                    getdouble(operacao["Valor"].replace(",", ".")),
                    '',
                    int(operacao["Quantidade"]),
                    '',
                    getdouble(operacao["Custos"].replace(',', '.')),
                    '',
                    '',
                    '',
                    '')
    updateAll()

def updateDayTrade():
    #Verifica papeis Distintos
    papeis = core.searchPapeisDistintos()  # le os papéis existentes em carteira
    #Para cada papel Distinto, verifica opaeração de compra e venda no mesmo dia
    for papel in papeis:
        operacoesPapel = core.searchPapelOrderedDateStatus(papel=papel)

        for operacaoPapel in operacoesPapel:

            compras = core.searchPapelDataStatus(   status="Compra",
                                                    papel=papel[0],
                                                    data=operacaoPapel[4])    #datetime.strptime(operacaoPapel[4], "%Y-%m-%d %H:%M:%S")
            vendas = core.searchPapelDataStatus(    status="Venda",
                                                    papel=papel[0],
                                                    data=operacaoPapel[4])
            #se a lista compras está vazia naquela data, para
            # aquele papel, não pode ter havido day-trade
            #e, se não há vendas, não tem o que ser atualizado para day-trade
            if compras and vendas: #daytrade
                for venda in vendas:
                    core.updateDayTrade(venda[0], 1)
                for compra in compras:
                    core.updateDayTrade(compra[0], 1)
            else: #não é daytrade
                for venda in vendas:
                     core.updateDayTrade(venda[0], 0)
                for compra in compras:
                    core.updateDayTrade(compra[0], 0)




#essa função é diferente da insert normal (que não servirá para nada agora)
#pois, ao inserir uma operação no DB, preco médio pm e posição consolidada devem ser computadas.
def calculaPmConsolidado(id, mercado, papel, status, data, valor , quantidade):
    #returns status, pm, qconsolidado
    rows = core.search2Insert(id, mercado, papel)
    #print(rows)
    if not rows:
        return "{:.2f}".format(round(0, 2)), 0

    elif len(rows) == 1:
        pmCalculado = valor
        consolidadoCalculado = quantidade
        return "{:.2f}".format(round(pmCalculado, 2)), consolidadoCalculado

    else:
        cont = 0
        for row in rows:
            if cont == 0: #estou na primeira linha
                pm = row[1]
                qconsolidado = row[2]
            else:
                pm = rows[cont - 1][1]
                qconsolidado = rows[cont - 1][2]

            if status == "Compra" and row[0] == "Compra":
                pmCalculado = ( pm * qconsolidado + valor * quantidade ) / (qconsolidado + quantidade)
                consolidadoCalculado = qconsolidado + quantidade
            elif status == "Venda" and row[0] == "Compra":
                consolidadoCalculado = qconsolidado - quantidade
                #if consolidadoCalculado == 0:
                #    pmCalculado = 0
                #else:
                pmCalculado = pm
            elif status == "Compra" and row[0] == "Venda":
                pmCalculado = ( pm * qconsolidado + valor * quantidade ) / (qconsolidado + quantidade)
                consolidadoCalculado = qconsolidado + quantidade
            else:
                consolidadoCalculado = qconsolidado - quantidade
                #if consolidadoCalculado == 0:
                #    pmCalculado = 0
                #else:
                pmCalculado = pm

            cont = cont + 1

    return "{:.2f}".format(round(pmCalculado,2)), consolidadoCalculado


#retorna tabela com a posição consolidada naquele mes dado pelos radio buttons
def posicaoConsolidadaMensal():
    dataCorreta, data, tipo = getDate()
    if tipo == 'MesAno':
        rows = core.consolidadoMensal(data.month,
                                  data.year)

def posicaoConsolidada2Pie():
    rows = core.searchPosicaoConsolidada("TRUE", 0)
    papels = []
    qconsolidado = []
    for row in rows:
        #print(row[2], "\t", row[10])
        papels.append(row[2])
        qconsolidado.append(row[13])#row[10] é a quantidade consolidada. row[13] é o valoratual
    return papels, qconsolidado



########Opens csv file to import stock data
def openFile():
    filename = askopenfilename(parent=app.window)
    f = open(filename)
    return f#.read()

def updatePieConsolidado():
    #updateValorAtual()
    app.ax1.clear()
    app.ax1.set_title("Posição Consolidada")
    #papels, qconsolidado = posicaoConsolidada2Pie() #faz o pie chart pelo qconsolidado em carteira
    dataFramePosicaoConsolidada = getCotacaoPapeisCarteira()
    posicoes = dataFramePosicaoConsolidada.values.transpose().tolist()[0]
    nomesPapeis = dataFramePosicaoConsolidada.index.transpose().tolist()
    app.ax1.pie(posicoes,
                labels=nomesPapeis,
                autopct='%1.1f%%',
                shadow=True,
                startangle=90)
    #app.ax2.legend(title="Posição Consolidada", bbox_to_anchor=(-.15, .85, 0, 0), loc="center left")
    app.ax1.axis('equal')
    #app.canvasCarteiraPie.flush_events()


def plotaCompCarteixaIbov(dataInicio, dataFim):
    iBovHistorico = inv.get_index_historical_data('Bovespa', country='brazil',
                                                  from_date=dataInicio, to_date=dataFim)

    #iBovDolarHistorico = inv.get_index_historical_data('Ibovespa USD', country='brazil',
    #                                              from_date=dataInicio, to_date=dataFim)

    #ifixHistorico = inv.get_index_historical_data('BM&FBOVESPA Real Estate IFIX', country='brazil',
    #                                              from_date=dataInicio, to_date=dataFim)

    indices = pd.DataFrame()
    normIbovIndex = iBovHistorico.index[0]
    normIbov = iBovHistorico['Close'].loc[normIbovIndex]
    indices['ibov'] = iBovHistorico['Close']/normIbov
    #indices['ibov_USD'] = iBovDolarHistorico['Close']/iBovDolarHistorico['Close'].loc[normalizador]

    carteira = historicoIndiceCarteira()

    if not app.varPapeis.get():
        carteira.drop(carteira.iloc[:, 0:len(carteira.columns)-1], inplace=True, axis=1)

    if app.varIbov.get():
        carteira = carteira.append(indices)
        #carteira = carteira.append(indices)
        #ndarrayIbov = indices['ibov'].values
        #ndarrayTranspose = np.asmatrix(ndarrayIbov).transpose()
        #listIbov = list(ndarrayTranspose)
        #seriesIbovNorm = pd.Series(listIbov, index=carteira.index)
        #carteira['Ibov'] = pd.Series(list(papelNormalizado), index=carteira.index)
        #seriesIbovNorm.index = carteira.index
        #carteira['Ibov'] = seriesIbovNorm
        #pd.Series(list(papelNormalizado), index=carteiraDetalhada.index)

    if not app.varCarteira.get():
        carteira.drop('Carteira', axis='columns', inplace=True)

    app.ax1Desempenho.clear()
    app.ax1Desempenho.plot(carteira)
    app.ax1Desempenho.legend(carteira.columns)
    app.toolbarDesempenho.update_idletasks()


def historicoIndiceCarteira():
    carteira = pd.DataFrame()
    carteiraDetalhada = pd.DataFrame()
    country = 'brazil'
    navegaPapel = 0
    itensCarteira = core.searchPapeisDistintos()#le os papéis existentes em carteira
    problemaData = FALSE
    for itemCarteira in itensCarteira:
        rows = core.searchPapel(itensCarteira[navegaPapel])#todas as operações no DB daquele papel
        navegaOperacao = 0
        seriesQConsolidado = pd.Series(dtype='float64')
        seriesPM = pd.Series(dtype='float64')
        seriesCotacao = pd.Series(dtype='float64')
        while navegaOperacao < len(rows):#varre até a penúltima operação daquele papel especificado
            iniciodate = datetime.strptime(rows[navegaOperacao][4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
            if len(rows) == 1:#há apenas uma entrada. fimDate é a data atual do dia
                fimdate = date.today().strftime("%d/%m/%Y")
            elif navegaOperacao == (len(rows) - 1) and rows[navegaOperacao][10] > 0: #última linha e ainda há posição
                fimdate = date.today().strftime("%d/%m/%Y")
            elif navegaOperacao == (len(rows) - 1) and rows[navegaOperacao][10] == 0: #última linha e não há posição
                fimdate = datetime.strptime(rows[navegaOperacao][4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
            else: #caso contrário, fimdate é sempre a data da próxima linha
                fimdate = datetime.strptime(rows[navegaOperacao + 1][4], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")


            #investpy requires fimDate > inicioDate
            if fimdate == iniciodate:
                fimdate = (datetime.strptime(rows[navegaOperacao][4], "%Y-%m-%d %H:%M:%S") \
                           + timedelta(days=1)).strftime("%d/%m/%Y")
                problemaData = TRUE
            try:
                tamSerie = seriesCotacao.size  # tamanho da série antes do append
                seriesHist = inv.get_stock_historical_data(itensCarteira[navegaPapel][0],
                                                      country=country,
                                                      from_date=iniciodate,
                                                      to_date=fimdate)['Close']
                if problemaData:
                    problemaData = FALSE
                    if len(seriesHist)==2:
                        seriesHist = seriesHist.drop(seriesHist.index[len(seriesHist)-1])

                qconsolidado = rows[navegaOperacao][10] #retorna qconsolidado da linha atual de processamento
                PMPapel = rows[navegaOperacao][8]       #retorna PM da linha atual de processamento


                #Appenda as 3 séries seriesCotacao, seriesQConsolidado, seriesPM
                #para os valores das novas datas
                seriesQConsolidado = seriesQConsolidado.append(#apenda qconsolidado
                                                            seriesHist/seriesHist * qconsolidado)
                seriesPM = seriesPM.append(                         #apenda o PM do papel faz a operação logica apenas pra
                                    seriesHist/seriesHist * PMPapel) # já criar a serie do tamanho correto
                seriesCotacao = seriesCotacao.append(seriesHist)


                # checa superposicoes de data e elimina-as, corrigindo a normalizacao
                #nas 3 séries necessárias para se calcular o índice de cada papel e da carteira
                #seriesCotacao, seriesQConsolidado, seriesPM
                if tamSerie > 1:
                    if seriesCotacao.index[tamSerie] == seriesCotacao.index[tamSerie - 1]:#datas duplicadas
                        idxtmp = seriesCotacao.index[tamSerie]
                        tmpCotacao = pd.Series([seriesCotacao[tamSerie]], index=[idxtmp])
                        tmpQConsolidado = pd.Series([seriesQConsolidado[tamSerie]], index=[idxtmp])
                        tmpPM = pd.Series([seriesPM[tamSerie]], index=[idxtmp])

                        seriesCotacao = seriesCotacao.drop(idxtmp)#dropa todoas as linhas indexadas pela data duplicada
                        seriesQConsolidado = seriesQConsolidado.drop(idxtmp)
                        seriesPM = seriesPM.drop(idxtmp)

                        seriesCotacao = seriesCotacao.append(tmpCotacao)
                        seriesQConsolidado = seriesQConsolidado.append(tmpQConsolidado)
                        seriesPM = seriesPM.append(tmpPM)

                        seriesCotacao = seriesCotacao.sort_index()
                        seriesQConsolidado = seriesQConsolidado.sort_index()
                        seriesPM = seriesPM.sort_index()

            except RuntimeError:
                print("Não achou o papel")
                seriesCotacao = pd.Series(dtype='float64')
                seriesQConsolidado = pd.Series(dtype='float64')
                seriesPM = pd.Series(dtype='float64')

            navegaOperacao = navegaOperacao + 1



        seriesCotacao.name = itemCarteira
        seriesQConsolidado.name = (itemCarteira, " qconsolidado")
        seriesPM.name = (itemCarteira, " PM")


        carteiraDetalhada[(itemCarteira, " qconsolidado")]  = seriesQConsolidado
        carteiraDetalhada[(itemCarteira, " cotacao")]       = seriesCotacao
        carteiraDetalhada[(itemCarteira, " PM")]            = seriesPM

        navegaPapel = navegaPapel + 1 #incrementa para pegar próximo papel


    carteiraDetalhada = carteiraDetalhada.fillna(0)

    posicaoAtualEmDinheiro = 0

    # logica para calcular papeis normalizados e
    # no dataFrame carteiraDetalhada
    valorCotacaoCarteira = 0
    valorPMCarteira = 0
    a = len(carteiraDetalhada.columns)
    b = a/3
    for cont in range(int(b)):
        qConsolidadoPapel       = carteiraDetalhada.iloc[:, 0+(cont*3):1+(cont*3)]  # Remember that Python does not slice inclusive of the ending index.
        cotacaoPapel            = carteiraDetalhada.iloc[:, 1+(cont*3):2+(cont*3)]  # Remember that Python does not slice inclusive of the ending index.
        PM                      = carteiraDetalhada.iloc[:, 2+(cont*3):3+(cont*3)]  # Remember that Python does not slice inclusive of the ending index.

        valorCotacaoPapel = cotacaoPapel.values * qConsolidadoPapel.values
        valorPMPapel = PM.values * qConsolidadoPapel.values
        papelNormalizado = valorCotacaoPapel / valorPMPapel

        carteira[itensCarteira[cont]] = pd.Series(list(papelNormalizado), index=carteiraDetalhada.index)

        #df['column_name'] = pd.Series(arr)

        valorCotacaoCarteira = valorCotacaoCarteira + cotacaoPapel.values * qConsolidadoPapel.values
        valorPMCarteira = valorPMCarteira + PM.values * qConsolidadoPapel.values

    carteiraNormalizada = valorCotacaoCarteira / valorPMCarteira


    #carteiraDetalhada['Carteira'] = pd.Series(list(carteiraNormalizada), index=carteiraDetalhada.index)
    carteira['Carteira'] = pd.Series(list(carteiraNormalizada), index=carteiraDetalhada.index)
    return carteira



def updateValorAtual():
    rows = core.viewAll() #retorna o banco de dados
    for row in rows:
        try:
            valorAtualPapel = inv.get_stock_information(    str(row[2]),
                                                            country='brazil')['Prev. Close']
            core.updateValorAtual(row[0], valorAtualPapel[0], '')
        except RuntimeError:
            print("Não achou o papel")



def updateDesempenho(): #todo pegar ultima data ao inves da data do dia pra evitar pau do invest.com
    if core.viewAll():
        plotaCompCarteixaIbov(datetime.strptime(core.searchLowestDate()[0][0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"),
                       date.today().strftime("%d/%m/%Y"))


def showAbout():
    messagebox.showinfo("CarteiraManager", "Versão 1.0\n Author: Odilon de Oliveira Dutra")


def populaIRPFs():
    populaIRPFRegular(calculaIRPFRegularMes(*getDate()))
    populaIRPFDT(calculaIRPFDayTrade(*getDate()))
    populaIRPFAnual(calculaIRPFAnual(*getDate()))

def populaIRPFRegular(vetorDadosIRPF):
    app.txtVendas.set("R$ {:.2f}".format(round(vetorDadosIRPF[0], 2)))
    app.txtIRPFRetidoFonte.set("R$ {:.2f}".format(round(vetorDadosIRPF[1], 2)))
    app.txtDespesasMensais.set("R$ {:.2f}".format(round(vetorDadosIRPF[2], 2)))
    app.txtLucroBruto.set("R$ {:.2f}".format(round(vetorDadosIRPF[3], 2)))
    app.txtImpostosDevidos.set("R$ {:.2f}".format(round(vetorDadosIRPF[4], 2)))
    app.txtLucroLiquido.set("R$ {:.2f}".format(round(vetorDadosIRPF[5], 2)))
    app.txtLucroLiquidoPercentual.set("{:.2f} %".format(round(vetorDadosIRPF[6], 2)))

def populaIRPFDT(vetorDadosIRPFDT):
    app.txtVendasDT.set("R$ {:.2f}".format(round(vetorDadosIRPFDT[0], 2)))
    app.txtIRPFRetidoFonteDT.set("R$ {:.2f}".format(round(vetorDadosIRPFDT[1], 2)))
    app.txtDespesasMensaisDT.set("R$ {:.2f}".format(round(vetorDadosIRPFDT[2], 2)))
    app.txtLucroBrutoDT.set("R$ {:.2f}".format(round(vetorDadosIRPFDT[3], 2)))
    app.txtImpostosDevidosDT.set("R$ {:.2f}".format(round(vetorDadosIRPFDT[4], 2)))
    app.txtLucroLiquidoDT.set("R$ {:.2f}".format(round(vetorDadosIRPFDT[5], 2)))
    app.txtLucroLiquidoPercentualDT.set("{:.2f} %".format(round(vetorDadosIRPFDT[6], 2)))

def populaIRPFAnual(vetorDadosIRPFAnual):
    app.txtVendasAnual.set("R$ {:.2f}".format(round(vetorDadosIRPFAnual[0], 2)))
    app.txtIRPFRetidoFonteAnual.set("R$ {:.2f}".format(round(vetorDadosIRPFAnual[1], 2)))
    app.txtDespesasMensaisAnual.set("R$ {:.2f}".format(round(vetorDadosIRPFAnual[2], 2)))
    app.txtLucroBrutoAnual.set("R$ {:.2f}".format(round(vetorDadosIRPFAnual[3], 2)))
    app.txtImpostosDevidosAnual.set("R$ {:.2f}".format(round(vetorDadosIRPFAnual[4], 2)))
    app.txtLucroLiquidoAnual.set("R$ {:.2f}".format(round(vetorDadosIRPFAnual[5], 2)))
    #app.txtLucroLiquidoPercentualAnual.set("{:.2f} %".format(round(vetorDadosIRPFAnual[6], 2)))
    app.txtLucroLiquidoVendasMaior20k.set("R$ {:.2f}".format(round(vetorDadosIRPFAnual[7], 2)))


#computa dados IRPF Regular Mensal
def calculaIRPFRegularMes(dataCorreta, data, tipo):
    aliquotaRegularRetidoFonte = 0.00005
    aliquotaRegular = 0.15
    limiteVendas = 20000

    if tipo == 'DiaMesAno' or tipo == 'MesAno':
        month = data.month
        year = data.year
        vendasMesRegulares = core.searchVendas("Vista", "Venda", month, year, dayTrade=0)
        operacoesMesRegulares = core.searchOperacoesMes("Vista", month, year, dayTrade=0)

        totalVendasMenosPMMes = 0
        totalvendasMes = 0
        despesasMensais = 0
        totalGanho = 0

        for row in vendasMesRegulares:
            totalVendasMenosPMMes = totalVendasMenosPMMes + (row[9] * (row[7] - row[8]))
            totalvendasMes = totalvendasMes + (row[9] * row[7])
            totalGanho = totalGanho + (row[9] * row[8])

        irpfRetidoFonte = aliquotaRegularRetidoFonte * totalvendasMes
        if irpfRetidoFonte < 1: #o IRPF retido na fonte é cobrado em cima da venda total apenas se
            irpfRetidoFonte = 0 #sua alíquota de 0,005% * totalVendas superar R$1,00

        for row in operacoesMesRegulares:
            despesasMensais = despesasMensais + row[11]

        #lucroBrutoMensal = totalVendasMenosPMMes - despesasMensais
        lucroBrutoMensal = totalVendasMenosPMMes

        if totalvendasMes < limiteVendas:
            impostoDevido = 0
        else:
            #impostoDevido = 0.15 * lucroBrutoMensal - irpfRetidoFonte
            impostoDevido = aliquotaRegular * (lucroBrutoMensal - despesasMensais) - irpfRetidoFonte

        #lucroLiquidoMensal = lucroBrutoMensal - impostoDevido
        lucroLiquidoMensal = lucroBrutoMensal - despesasMensais - impostoDevido
        if totalGanho != 0:
            lucroLiquidoPercentual = round(100 * lucroLiquidoMensal / totalGanho, 2)
        else:
            lucroLiquidoPercentual = 0

    return [totalvendasMes,
            irpfRetidoFonte,
            despesasMensais,
            lucroBrutoMensal,
            impostoDevido,
            lucroLiquidoMensal,
            lucroLiquidoPercentual]


#computa dados IRPF DT Mensal
def calculaIRPFDayTrade(dataCorreta, data, tipo):
    aliquotaDayTradeRetidoFonte = 0.01
    aliquotaDayTrade = 0.20
    if tipo == 'DiaMesAno' or tipo == 'MesAno':
        month = data.month
        year = data.year
        vendasMesDayTrade = core.searchVendas("Vista", "Venda", month, year, dayTrade=1)
        operacoesMesDayTrade = core.searchOperacoesMes("Vista", month, year, dayTrade=1)

        totalVendasMenosPMMes = 0
        totalvendasMes = 0
        despesasMensais = 0
        totalGanho = 0

        for row in vendasMesDayTrade:
            totalVendasMenosPMMes = totalVendasMenosPMMes + (row[9] * (row[7] - row[8]))
            totalvendasMes = totalvendasMes + (row[9] * row[7])
            totalGanho = totalGanho + (row[9] * row[8])

        irpfRetidoFonte = aliquotaDayTradeRetidoFonte * totalvendasMes
        if irpfRetidoFonte < 1:  # o IRPF retido na fonte é cobrado em cima da venda total apenas se
            irpfRetidoFonte = 0  # sua alíquota de 0,005% * totalVendas superar R$1,00

        for row in operacoesMesDayTrade:
            despesasMensais = despesasMensais + row[11]

        # lucroBrutoMensal = totalVendasMenosPMMes - despesasMensais
        lucroBrutoMensal = totalVendasMenosPMMes

        if lucroBrutoMensal < 0:
            impostoDevido = 0
        else:
            # impostoDevido = 0.15 * lucroBrutoMensal - irpfRetidoFonte
            impostoDevido = aliquotaDayTrade * (lucroBrutoMensal - despesasMensais) - irpfRetidoFonte

        # lucroLiquidoMensal = lucroBrutoMensal - impostoDevido
        lucroLiquidoMensal = lucroBrutoMensal - despesasMensais - impostoDevido
        #app.txtLucroLiquidoDT.set("R$ {:.2f}".format(round(lucroLiquidoMensal, 2)))
        if totalGanho != 0:
            lucroLiquidoPercentual = round(100 * lucroLiquidoMensal / totalGanho, 2)
        else:
            lucroLiquidoPercentual = 0

        return [totalvendasMes,
                irpfRetidoFonte,
                despesasMensais,
                lucroBrutoMensal,
                impostoDevido,
                lucroLiquidoMensal,
                lucroLiquidoPercentual]

#computa as informacoes de IR, para todos os meses acumulados até o mês
#informado. Se colocado mês de Dezembro, computa as informações daquele ano.
def calculaIRPFAnual(dataCorreta, data, tipo):
    if tipo == 'DiaMesAno' or tipo == 'MesAno':
        month = data.month
        year = data.year
        mes = 1
        tipo = 'MesAno'
        dadosIRPFRegular = []
        dadosIRPFDT = []
        dadosIRPFRegular = [0 for i in range(7)]
        dadosIRPFDT = [0 for i in range(7)]
        dadosIRPFAnual = [0 for i in range(8)]
        app.txtLabelFrameIRPFAnual.set("IRPF Acumulado até "+ str(month) + "/" + str(year))
        app.frameIRPFAnual.configure(text=app.txtLabelFrameIRPFAnual.get())


        for mes in range(1, month+1):
            a = str(mes)+"/"+str(year)
            dataAtual = datetime.strptime(str(mes)+"/"+str(year), '%m/%Y')

            tmp = calculaIRPFRegularMes(dataCorreta, dataAtual, tipo)
            if tmp[4] == 0: #não houve IRPF a se recolher no mes
                #a = np.append(tmp, [0])
                #b = np.append(dadosIRPFAnual, 0)
                dadosIRPFAnual = np.add(dadosIRPFAnual, np.append(tmp, [0]))
            else: #houve recolhimento de IRPF naquele mês
                dadosIRPFAnual = [dadosIRPFAnual[0] + tmp[0], #totalvendasAno
                                  dadosIRPFAnual[1] + tmp[1], #irpfRetidoFonteAno
                                  dadosIRPFAnual[2] + tmp[2], #despesasAnuais
                                  dadosIRPFAnual[3] + tmp[3], #lucroBrutoAnual
                                  dadosIRPFAnual[4] + tmp[4], #impostoDevidoAnual
                                  dadosIRPFAnual[5] + 0, #lucroLiquidoAnual
                                  dadosIRPFAnual[6] + tmp[6], #lucroLiquidoPercentualAnual
                                  dadosIRPFAnual[7] + tmp[5], #lucroLiquidoVendasMaior20k
                                ]

            tmpDT = calculaIRPFDayTrade(dataCorreta, dataAtual, tipo)
            dadosIRPFAnual = [dadosIRPFAnual[0] + tmpDT[0],  # totalvendasAno
                              dadosIRPFAnual[1] + tmpDT[1],  # irpfRetidoFonteAno
                              dadosIRPFAnual[2] + tmpDT[2],  # despesasAnuais
                              dadosIRPFAnual[3] + tmpDT[3],  # lucroBrutoAnual
                              dadosIRPFAnual[4] + tmpDT[4],  # impostoDevidoAnual
                              dadosIRPFAnual[5] + 0,         # lucroLiquidoAnual
                              dadosIRPFAnual[6] + tmpDT[6],  # lucroLiquidoPercentualAnual
                              dadosIRPFAnual[7] + tmpDT[5],  # lucroLiquidoVendasMaior20k
                              ]
                    #dadosIRPFAnual = dadosIRPFRegular + dadosIRPFDT
        return dadosIRPFAnual
        # return [totalvendasAno,
        #         irpfRetidoFonteAno,
        #         despesasAnuais,
        #         lucroBrutoAnual,
        #         impostoDevidoAnual,
        #         lucroLiquidoAnual,
        #         lucroLiquidoPercentualAnual,
        #         lucroLiquidoVendasMaior20k]


def getDate():
    #if app.txtData.get():
    try:
        data = datetime.strptime(app.txtData.get(), '%d/%m/%Y')
        correctDate = True
        tipo = 'DiaMesAno'
    except ValueError:
        correctDate = False
        tipo = ''

    if correctDate == False:
        try:
            data = datetime.strptime(app.txtData.get(), '%m/%Y')
            correctDate = True
            tipo = 'MesAno'
        except ValueError:
            correctDate = False
            tipo = ''

    if correctDate == False:
        try:
            data = datetime.strptime(app.txtData.get(), '%Y')
            correctDate = True
            tipo = 'Ano'
        except ValueError:
            correctDate = False
            data = False
            tipo = ''

    if tipo == '' and app.txtData.get() != '':
        messagebox.showwarning("Aviso:", "Data deve estar em um dos seguintes formatos:\n " +
                               "dd/mm/aaaa, ou mm/aaaa, ou aaaa")

    return correctDate, data, tipo

def getCotacaoPapeisCarteira():
    rows = core.searchPosicaoConsolidada("TRUE", 0)
    posicao = pd.Series(dtype='float64')
    serieValue = pd.Series(dtype='float64')
    serieIndex = pd.Series(dtype='float64')
    for row in rows:
        try:
            cotacao = inv.get_stock_information(    str(row[2]),
                                                    country='brazil')['Prev. Close']
            serieValue = serieValue.append((row[10] * cotacao), ignore_index=True)
            serieIndex = serieIndex.append(pd.Series(row[2]), ignore_index=True)
        except ValueError:
            print("ValueError Exception. Não achou o papel: " + row[2])
            messagebox.showwarning("ValueError Exception.",
                                   "Papel " + row[2] + "não foi encontrado na base de dados Invest")
        except RuntimeError:
            print("RunTime Exception", "Tente novamente. Ativo: " + row[2])
            messagebox.showwarning("RunTime Exception",
                                   "Tente novamente. " + row[2])
    posicao = pd.DataFrame(serieValue)
    posicao.set_index(serieIndex, inplace=True)
    return posicao


def getIndicadoresTecnicos(papel):
    try:
        indicadores = inv.technical_indicators(   papel,
                                                country='brazil',
                                                product_type='stock')
        cont = 0
        app.textAreaIndicators.delete('1.0', END)
        for row in indicadores["technical_indicator"]:
            strIndicadores = (str(row) + " / "
                            + str(indicadores["value"][cont]) + " / "
                            + str(indicadores["signal"][cont]) + "\n")
            app.textAreaIndicators.insert(INSERT, strIndicadores)
            cont = cont + 1
    except ValueError:
        app.textAreaIndicators.delete('1.0', END)
        app.textAreaIndicators.insert(INSERT, 'ValueError Exception. Papel não encontrado no Invest.com')
    except RuntimeError:
        app.textAreaIndicators.delete('1.0', END)
        app.textAreaIndicators.insert(INSERT, 'RunTime Exception. Tente novamente. ')


def getIndicadoresFundamentalistas(papel):
    try:
        indicadores = inv.get_stock_information(papel, country='brazil')
        tmp = []
        tmp.append(str(("Beta = " + str(indicadores['Beta'][0]) + "\n")))
        tmp.append(str(("1-Year Change = " + str(indicadores['1-Year Change'][0]) + "\n")))
        tmp.append(str(("Next Earnings Date = " + str(indicadores['Next Earnings Date'][0]) + "\n")))
        tmp.append(str(("P/E Ratio = " + str(indicadores['P/E Ratio'][0]) + "\n")))
        tmp.append(str(("Dividend (Yield) = " + str(indicadores['Dividend (Yield)'][0]) + "\n")))
        tmp.append(str(("EPS = " + str(indicadores["EPS"][0]) + "\n")))
        tmp.append(str(("52 wk Range = " + str(indicadores['52 wk Range'][0]) + "\n")))
        tmp.append(str(("Todays Range = " + str(indicadores['Todays Range'][0]) + "\n")))
        tmp.append(str(("Prev. Close = " + str(indicadores['Prev. Close'][0]) + "\n")))
        tmp.append(str(("Open = " + str(indicadores['Open'][0]))))
        app.textAreaIndicatorsFund.delete('1.0', END)
        for row in tmp:
            app.textAreaIndicatorsFund.insert(INSERT, row)
    except ValueError:
        app.textAreaIndicatorsFund.delete('1.0', END)
        app.textAreaIndicatorsFund.insert(INSERT, 'Papel não encontrado no Invest.com')
    except RuntimeError:
        app.textAreaIndicatorsFund.delete('1.0', END)
        app.textAreaIndicatorsFund.insert(INSERT, 'Algum problema aconteceu. Tente novamente. ')

def iniciaThreadDesempenho():
    # th = threading.Thread(target=updateDesempenho)  # atualiza os charts numa thread diferent pois demora pra
    #                                                 #baixar os dados do invest.py
    # if not th.is_alive():
    #     try:
    #         th.start()
    #     except RuntimeError:  # occurs if thread is dead
    #         th = threading.Thread(target=updateDesempenho)  # create new instance if thread is dead
    #         th.start()
    def real_iniciaThreadDesempenho():
        app.progressDesempenho.grid(row=0, column=0, columnspan=3, sticky='nesw', padx=250, pady=250)
        app.progressDesempenho.lift()
        app.progressDesempenho.start()
        updateDesempenho()#time.sleep(5)
        app.progressDesempenho.stop()
        app.progressDesempenho.grid_forget()
        app.btnUpdateDesempenho['state'] = 'normal'
    app.btnUpdateDesempenho['state'] = 'disabled'
    threading.Thread(target=real_iniciaThreadDesempenho).start()



def iniciaThreadPie():
    # th = threading.Thread(target=updatePieConsolidado)  # atualiza os charts numa thread diferent pois demora pra
    # # baixar os dados do invest.py
    # if not th.is_alive():
    #     try:
    #         th.start()
    #     except RuntimeError:  # occurs if thread is dead
    #         th = threading.Thread(target=updatePieConsolidado)  # create new instance if thread is dead
    #         th.start()
    def real_iniciaThreadPie():
        app.progressPIE.grid(row=0, column=0, sticky='nesw', columnspan=3, padx=250, pady=250)
        app.progressPIE.lift()
        app.progressPIE.start()
        updatePieConsolidado()#time.sleep(5)
        app.progressPIE.stop()
        app.progressPIE.grid_forget()
        app.btnUpdatePie['state'] = 'normal'
    app.btnUpdatePie['state'] = 'disabled'
    threading.Thread(target=real_iniciaThreadPie).start()


if __name__ == "__main__":
    app = Gui()
    app.listPapels.bind('<<TreeviewSelect>>', getSelectedRow)
    app.btnViewAll.configure(command=view_command)
    app.btnBuscar.configure(command=search_command)
    app.btnInserir.configure(command=insert_command)#insert_command)
    app.btnDel.configure(command=del_command)
    app.btnClose.configure(command=app.window.destroy)
    #app.btnCalculaIRPFMensal.configure(command=populaIRPFs)
    #app.btnCalculaIRPFMensalDetalhes.configure(command=detalhaIRPF)
    app.btnCalculaIRPFAnual.configure(command=populaIRPFs)

    app.btnUpdatePie.configure(command=iniciaThreadPie)
    app.btnUpdateDesempenho.configure(command=iniciaThreadDesempenho)

    app.filemenu.add_command(label="Import CSV", command=importCSV)
    app.filemenu.add_command(label="Export CSV", command=exportCSV)
    app.filemenu.add_separator()
    app.filemenu.add_command(label="Exit", command=app.window.quit)
    app.helpmenu.add_command(label="About", command=showAbout)

    iniciaThreadPie()
    app.run()
