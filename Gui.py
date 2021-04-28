from tkinter import *
from tkinter import ttk
#import tkfontchooser
import ToolTip
#from tkcalendar import *
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plot
#matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
#from matplotlib.figure import Figure

class Gui:
    """Classe que define a interface gráfica da aplicação
    """
    x_pad = 5
    y_pad = 3

    #Criando a janela...
    window          = Tk()
    window.wm_title("Cadastro de Ações")
    window.geometry('1780x990')
    #mono_font = tkfontchooser.Font(family="Arial", size=18)
    #mono_font_IRPF = tkfontchooser.Font(family="Arial", size=16)
    #mono_font_Indicadores = tkfontchooser.Font(family="Arial", size=15)




    # Criando Menus
    menubar = Menu(window)
    filemenu = Menu(menubar, tearoff=0)
    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=filemenu)
    menubar.add_cascade(label="Help", menu=helpmenu)
    window.config(menu=menubar)








    ##############################################################################################
    #####################Frame Controles Principais - frameButoes#################################
    ##############################################################################################
    frameButoes = LabelFrame(window, text="Controles")
    # Criando variáveis que armazenarão o texto inserido pelo usuário...
    txtMercado = StringVar()
    txtPapel = StringVar()
    txtStatus = StringVar()
    txtData = StringVar()
    txtValorCompra = StringVar()
    txtQuantidade = StringVar()
    txtCustos = StringVar()
    varBusca = IntVar()
    #Criando os objetos que estarão na janela...
    lblMercado      = Label(frameButoes, text="Mercado") #, font=mono_font)
    lblPapel        = Label(frameButoes, text="Ação") #, font=mono_font)
    lblStatus       = Label(frameButoes, text="Status") #, font=mono_font)
    lblData         = Label(frameButoes, text="Data") #, font=mono_font)
    lblValorCompra  = Label(frameButoes, text="Valor") #, font=mono_font)
    lblQuantidade   = Label(frameButoes, text="Quantidade") #, font=mono_font)
    lblCustos       = Label(frameButoes, text="Custos") #, font=mono_font)
    #Criando campos de Input
    comboMercado = ttk.Combobox(frameButoes, values=[
                                        "Vista",
                                        "Opções"],
                                    state="Vista",
                                    textvariable=txtMercado) #, font=mono_font)
    entPapel        = Entry(frameButoes,
                            textvariable=txtPapel)# , font=mono_font)
    comboStatus = ttk.Combobox(frameButoes, values=[
                                        "Compra",
                                        "Venda"],
                               state="Compra",
                               textvariable=txtStatus) #, font=mono_font)
    entData         = Entry(frameButoes, textvariable=txtData) #, font=mono_font)
    entValor        = Entry(frameButoes, textvariable=txtValorCompra) #, font=mono_font)
    entQuantidade   = Entry(frameButoes, textvariable=txtQuantidade) #, font=mono_font)
    entCustos       = Entry(frameButoes, textvariable=txtCustos) #, font=mono_font)
    #Criando Botoes
    btnViewAll     = Button(frameButoes, text="Ver todos") #, font=mono_font)
    btnBuscar      = Button(frameButoes, text="Buscar") #, font=mono_font)
    btnInserir     = Button(frameButoes, text="Inserir") #, font=mono_font)
    #btnUpdate      = Button(frameButoes, text="Atualizar Selecionado") #, font=mono_font)
    btnDel         = Button(frameButoes, text="Deletar Selecionado") #, font=mono_font)
    btnClose       = Button(frameButoes, text="Fechar") #, font=mono_font)
    ############################### Arranjo dos WIdgets###########################################
    lblMercado.grid(row=0, column=0, sticky=E)
    lblStatus.grid(row=1, column=0, sticky=E)
    lblPapel.grid(row=2, column=0, sticky=E)
    lblData.grid(row=3, column=0, sticky=E)
    lblValorCompra.grid(row=4, column=0, sticky=E)
    lblQuantidade.grid(row=5, column=0, sticky=E)
    lblCustos.grid(row=6, column=0, sticky=E)
    comboMercado.grid(row=0, column=1)#, padx=10, pady=50)
    comboStatus.grid(row=1, column=1)
    entPapel.grid(row=2, column=1)
    entData.grid(row=3, column=1)
    entValor.grid(row=4, column=1)
    entQuantidade.grid(row=5, column=1)
    entCustos.grid(row=6, column=1)
    btnViewAll.grid(row=7, column=0, columnspan=2, sticky='nesw')  # 7
    btnBuscar.grid(row=8, column=0, columnspan=2, sticky='nesw')
    btnInserir.grid(row=9, column=0, columnspan=2, sticky='nesw')
    #btnUpdate.grid(row=10, column=0, columnspan=2, sticky='nesw')
    btnDel.grid(row=11, column=0, columnspan=2, sticky='nesw')
    ##############################################################################################
    #####################Fim Frame Controle Principais - frameButoes##############################
    ##############################################################################################







    ##############################################################################################
    #################################Frame listPapels - frameList#################################
    ##############################################################################################
    # Criando ListaTkTreectrl e ScrollBar
    frameList = LabelFrame(window, text='')  # "Labels das colunas e a lista e a scroll bar
    listPapels = ttk.Treeview(frameList, height=19)
    listPapels.tag_configure("impar", background="#cccccc")
    listPapels.tag_configure("par", background="#ffffff")
    listPapels["columns"] = (
        "Papel",
        "Status",
        "Data",
        "Preço",
        "PM",
        "N",
        "NC",
        "Custos")
    listPapels.column("#0", width=80)
    listPapels.column("Papel", width=70)
    listPapels.column("Status", width=70)
    listPapels.column("Data", width=80)
    listPapels.column("Preço", width=80)
    listPapels.column("PM", width=80)
    listPapels.column("N", width=70)
    listPapels.column("NC", width=70)
    listPapels.column("Custos", width=70)
    listPapels.heading("#0", text="MKT", anchor=W)
    listPapels.heading("Papel", text="Papel", anchor=W)
    listPapels.heading("Status", text="Status", anchor=W)
    listPapels.heading("Data", text="Data", anchor=W)
    listPapels.heading("Preço", text="Preço", anchor=W)
    listPapels.heading("PM", text="PM", anchor=W)
    listPapels.heading("N", text="N", anchor=W)
    listPapels.heading("NC", text="NC", anchor=W)
    listPapels.heading("Custos", text="Custos", anchor=W)
    scrollPapelsY = Scrollbar(frameList)
    scrollPapelsX = Scrollbar(frameList, orient=HORIZONTAL)
    # Associando a Scrollbar com a Listbox...
    listPapels.configure(yscrollcommand=scrollPapelsY.set, xscrollcommand=scrollPapelsX.set)
    scrollPapelsY.configure(command=listPapels.yview)
    scrollPapelsX.configure(command=listPapels.xview)
    ############################### Arranjo dos WIdgets###########################################
    listPapels.grid(row=0, column=0, rowspan=1, columnspan=3, sticky='nesw')
    scrollPapelsY.grid(row=0, column=3, rowspan=1, sticky='nes')
    scrollPapelsX.grid(row=1, column=3, rowspan=1, sticky='nesw')
    ##############################################################################################
    ##############################Fim Frame listPapels - frameList################################
    ##############################################################################################













    # Frame to Exbit both IRPF Day-Trade and regular for the chosen month
    txtLabelFrameBoth = "IRPF"
    frameIRPFBoth = LabelFrame(window, text=txtLabelFrameBoth, padx=5, pady=10)  # ) #, font=mono_font_IRPF)
    btnCalculaIRPFMensal = Button(frameIRPFBoth,
                                  text="Calcula IRPF Mensal")  # , font=mono_font)
    btnCalculaIRPFMensal.grid(row=1, column=0, columnspan=2, sticky='nesw')
    ##############################################################################################
    #################################Frame IRPF Regular - frameIRPF#################################
    ##############################################################################################
    txtLabelFrame = StringVar()
    txtMercadoIRPF = StringVar()
    txtVendas = StringVar()
    txtLucroBruto = StringVar()
    txtLucroLiquido = StringVar()
    txtLucroLiquidoPercentual = StringVar()
    txtImpostosDevidos = StringVar()
    txtIRPFRetidoFonte = StringVar()
    txtDespesasMensais = StringVar()

    txtLabelFrame = "IRPF Regular Mensal"
    frameIRPF = LabelFrame(frameIRPFBoth, text=txtLabelFrame, width=5)  # , padx=20, pady=20)
    labelMercado = Label(frameIRPF, text="Mercado")  # , font=mono_font_IRPF)
    labelVendas = Label(frameIRPF, text="Vendas")  # , font=mono_font_IRPF)
    labelLucroBruto = Label(frameIRPF, text="L. Bruto")  # , font=mono_font_IRPF)
    labelDespesasMensais = Label(frameIRPF, text="Despesas")  # , font=mono_font_IRPF)
    labelLucroLiquido = Label(frameIRPF, text="L. Líquido")  # , font=mono_font_IRPF)
    labelLucroLiquidoPercentual = Label(frameIRPF, text="L. Líquido %")  # , font=mono_font_IRPF)
    labelIRPFRetido = Label(frameIRPF, text="IRPF Retido")  # , font=mono_font_IRPF)
    labelImpostosDevidos = Label(frameIRPF, text="IRPF Devido")  # , font=mono_font_IRPF)

    # entMercadoIRPF = Entry(frameIRPF, textvariable=txtMercadoIRPF, state='disabled', width=2)
    entVendas = Entry(frameIRPF, textvariable=txtVendas, state='disabled', width=12)  # , font=mono_font_IRPF)
    entLucroBruto = Entry(frameIRPF, textvariable=txtLucroBruto, state='disabled', width=12)  # , font=mono_font_IRPF)
    entDespesasMensais = Entry(frameIRPF, textvariable=txtDespesasMensais, state='disabled',
                               width=12)  # , font=mono_font_IRPF)
    entLucroLiquido = Entry(frameIRPF, textvariable=txtLucroLiquido, state='disabled',
                            width=12)  # , font=mono_font_IRPF)
    entLucroLiquidoPercentual = Entry(frameIRPF, textvariable=txtLucroLiquidoPercentual, state='disabled',
                                      width=12)  # , font=mono_font_IRPF)
    entIRPFRetido = Entry(frameIRPF, textvariable=txtIRPFRetidoFonte, state='disabled',
                          width=12)  # , font=mono_font_IRPF)
    entImpostosDevidos = Entry(frameIRPF, textvariable=txtImpostosDevidos, state='disabled',
                               width=12)  # , font=mono_font_IRPF)

    ToolTip.CreateToolTip(labelLucroBruto, text="Lucro antes de descontar \n"
                                                "taxas de operação, corretagem, etc \n"
                                                "e impostos.\n"
                                                "No programa de IRPF, caso as vendas do \n"
                                                "mês ultrapassarem R$20.000,00, lancar em renda\n"
                                                "variável o valor do Lucro Bruto - Desepsas.\n"
                                                "Caso contrário, lançar o somatório desse mesmo valor, \n"
                                                "para todos os meses em que Vendas < R$20.000,00, em\n"
                                                "Rendimentos Isentos e Não Tributáveis, classe 20")

    ToolTip.CreateToolTip(labelDespesasMensais, text="Despesas operacionais:\n"
                                                     "taxas de operação, corretagem, \n"
                                                     "emolumentos, etc")

    ToolTip.CreateToolTip(labelLucroLiquido, text="Lucro Bruto - Despesas - Impostos. \n"
                                                  "No programa de IRPF, caso as vendas do \n"
                                                  "mês ultrapassarem R$20.000,00, lancar em renda\n"
                                                  "variável o valor do Lucro Bruto - Desepsas.\n"
                                                  "Caso contrário, lançar o somatório desse mesmo valor, \n"
                                                  "para todos os meses em que Vendas < R$20.000,00, em\n"
                                                  "Rendimentos Isentos e Não Tributáveis, classe 20")

    ToolTip.CreateToolTip(labelIRPFRetido, text="Imposto retido na fonte pela corretora.\n"
                                                "Lançar esse valor no programa de IRPF, \n"
                                                "area de Renda Variável, para o referido mês.\n"
                                                "É o dedo-duro para a receita checar os valores.\n"
                                                "Conferir valor reportado pela corretora com\n"
                                                "o desse programa.")

    ############################### Arranjo dos WIdgets###########################################
    labelVendas.grid(row=1, column=0, sticky='e')
    labelLucroBruto.grid(row=2, column=0, sticky='e')
    labelDespesasMensais.grid(row=3, column=0, sticky='e')
    labelLucroLiquido.grid(row=4, column=0, sticky='e')
    labelLucroLiquidoPercentual.grid(row=5, column=0, sticky='e')
    labelIRPFRetido.grid(row=6, column=0, sticky='e')
    labelImpostosDevidos.grid(row=7, column=0, sticky='e')
    entVendas.grid(row=1, column=1, sticky='nesw')
    entLucroBruto.grid(row=2, column=1, sticky='nesw')
    entDespesasMensais.grid(row=3, column=1, sticky='nesw')
    entLucroLiquido.grid(row=4, column=1, sticky='nesw')
    entLucroLiquidoPercentual.grid(row=5, column=1, sticky='nesw')
    entIRPFRetido.grid(row=6, column=1, sticky='nesw')
    entImpostosDevidos.grid(row=7, column=1, sticky='nesw')

    # Os frames abaixo estão linkados no frameIRPFBoth
    frameIRPF.grid(row=0, column=0, sticky='nesw')
    frameIRPF.columnconfigure(0, weight=1)
    ##############################################################################################
    ##############################Fim Frame IRPF Regular - frameIRPF##############################
    ##############################################################################################












    ##############################################################################################
    #################################Frame IRPF DT - frameIRPF#################################
    ##############################################################################################
    txtMercadoIRPFDT = StringVar()
    txtVendasDT = StringVar()
    txtLucroBrutoDT = StringVar()
    txtLucroLiquidoDT = StringVar()
    txtLucroLiquidoPercentualDT = StringVar()
    txtImpostosDevidosDT = StringVar()
    txtIRPFRetidoFonteDT = StringVar()
    txtDespesasMensaisDT = StringVar()

    # Frame to Exbit due IRPF Day-Trade for the chosen month
    txtLabelFrameDayTrade = "IRPF DayTrade Mensal"
    frameIRPFDayTrade = LabelFrame(frameIRPFBoth, text=txtLabelFrameDayTrade)  # , padx=20, pady=20)

    labelMercadoDT = Label(frameIRPFDayTrade, text="Mercado")  # , font=mono_font_IRPF)
    labelVendasDT = Label(frameIRPFDayTrade, text="Vendas")  # , font=mono_font_IRPF)
    labelLucroBrutoDT = Label(frameIRPFDayTrade, text="L. Bruto")  # , font=mono_font_IRPF)
    labelDespesasMensaisDT = Label(frameIRPFDayTrade, text="Despesas")  # , font=mono_font_IRPF)
    labelLucroLiquidoDT = Label(frameIRPFDayTrade, text="L. Líquido")  # , font=mono_font_IRPF)
    labelLucroLiquidoPercentualDT = Label(frameIRPFDayTrade, text="L. Líquido %")  # , font=mono_font_IRPF)
    labelIRPFRetidoDT = Label(frameIRPFDayTrade, text="IRPF Retido")  # , font=mono_font_IRPF)
    labelImpostosDevidosDT = Label(frameIRPFDayTrade, text="IRPF Devido")  # , font=mono_font_IRPF)

    entMercadoIRPFDT = Entry(frameIRPFDayTrade, textvariable=txtMercadoIRPFDT, state='disabled',
                             width=12)  # , font=mono_font_IRPF)
    entVendasDT = Entry(frameIRPFDayTrade, textvariable=txtVendasDT, state='disabled',
                        width=12)  # , font=mono_font_IRPF)
    entLucroBrutoDT = Entry(frameIRPFDayTrade, textvariable=txtLucroBrutoDT, state='disabled',
                            width=12)  # , font=mono_font_IRPF)
    entDespesasMensaisDT = Entry(frameIRPFDayTrade, textvariable=txtDespesasMensaisDT, state='disabled',
                                 width=12)  # , font=mono_font_IRPF)
    entLucroLiquidoDT = Entry(frameIRPFDayTrade, textvariable=txtLucroLiquidoDT, state='disabled',
                              width=12)  # , font=mono_font_IRPF)
    entLucroLiquidoPercentualDT = Entry(frameIRPFDayTrade, textvariable=txtLucroLiquidoPercentualDT, state='disabled',
                                        width=12)  # , font=mono_font_IRPF)
    entIRPFRetidoDT = Entry(frameIRPFDayTrade, textvariable=txtIRPFRetidoFonteDT, state='disabled',
                            width=12)  # , font=mono_font_IRPF)
    entImpostosDevidosDT = Entry(frameIRPFDayTrade, textvariable=txtImpostosDevidosDT, state='disabled',
                                 width=12)  # , font=mono_font_IRPF)

    ############################### Arranjo dos WIdgets###########################################
    labelVendasDT.grid(row=1, column=0, sticky='e')
    labelLucroBrutoDT.grid(row=2, column=0, sticky='e')
    labelDespesasMensaisDT.grid(row=3, column=0, sticky='e')
    labelLucroLiquidoDT.grid(row=4, column=0, sticky='e')
    labelLucroLiquidoPercentualDT.grid(row=5, column=0, sticky='e')
    labelIRPFRetidoDT.grid(row=6, column=0, sticky='e')
    labelImpostosDevidosDT.grid(row=7, column=0, sticky='e')
    entVendasDT.grid(row=1, column=1, sticky='nesw')
    entLucroBrutoDT.grid(row=2, column=1, sticky='nesw')
    entDespesasMensaisDT.grid(row=3, column=1, sticky='nesw')
    entLucroLiquidoDT.grid(row=4, column=1, sticky='nesw')
    entLucroLiquidoPercentualDT.grid(row=5, column=1, sticky='nesw')
    entIRPFRetidoDT.grid(row=6, column=1, sticky='nesw')
    entImpostosDevidosDT.grid(row=7, column=1, sticky='nesw')
    #Os frames abaixo estão linkados no frameIRPFBoth
    frameIRPFDayTrade.grid(row=0, column=1, sticky='nesw')
    frameIRPFDayTrade.columnconfigure(0, weight=1)
    ##############################################################################################
    ##############################Fim Frame IRPF DT - frameIRPF##############################
    ##############################################################################################





    ##############################################################################################
    #################################Frame IRPF Anual - frameIRPFAnual############################
    ##############################################################################################
    txtMercadoIRPFAnual = StringVar()
    txtVendasAnual = StringVar()
    txtLucroBrutoAnual = StringVar()
    txtLucroLiquidoAnual = StringVar()
    txtLucroLiquidoPercentualAnual = StringVar()
    txtImpostosDevidosAnual = StringVar()
    txtIRPFRetidoFonteAnual = StringVar()
    txtDespesasMensaisAnual = StringVar()

    # Frame to Exbit due IRPF Anual for the chosen year
    txtLabelFrameIRPFAnual = "IRPF Anual"
    frameIRPFAnual = LabelFrame(frameIRPFBoth, text=txtLabelFrameIRPFAnual)  # , padx=20, pady=20)

    labelMercadoAnual = Label(frameIRPFAnual, text="Mercado")  # , font=mono_font_IRPF)
    labelVendasAnual = Label(frameIRPFAnual, text="Vendas")  # , font=mono_font_IRPF)
    labelLucroBrutoAnual = Label(frameIRPFAnual, text="L. Bruto")  # , font=mono_font_IRPF)
    labelDespesasMensaisAnual = Label(frameIRPFAnual, text="Despesas")  # , font=mono_font_IRPF)
    labelLucroLiquidoAnual = Label(frameIRPFAnual, text="L. Líquido")  # , font=mono_font_IRPF)
    labelLucroLiquidoPercentualAnual = Label(frameIRPFAnual, text="L. Líquido %")  # , font=mono_font_IRPF)
    labelIRPFRetidoAnual = Label(frameIRPFAnual, text="IRPF Retido")  # , font=mono_font_IRPF)
    labelImpostosDevidosAnual = Label(frameIRPFAnual, text="IRPF Devido")  # , font=mono_font_IRPF)

    entMercadoIRPFAnual= Entry(frameIRPFAnual, textvariable=txtMercadoIRPFAnual, state='disabled',
                             width=12)  # , font=mono_font_IRPF)
    entVendasAnual = Entry(frameIRPFAnual, textvariable=txtVendasAnual, state='disabled',
                        width=12)  # , font=mono_font_IRPF)
    entLucroBrutoAnual = Entry(frameIRPFAnual, textvariable=txtLucroBrutoAnual, state='disabled',
                            width=12)  # , font=mono_font_IRPF)
    entDespesasMensaisAnual = Entry(frameIRPFAnual, textvariable=txtDespesasMensaisAnual, state='disabled',
                                 width=12)  # , font=mono_font_IRPF)
    entLucroLiquidoAnual = Entry(frameIRPFAnual, textvariable=txtLucroLiquidoAnual, state='disabled',
                              width=12)  # , font=mono_font_IRPF)
    entLucroLiquidoPercentualAnual = Entry(frameIRPFAnual, textvariable=txtLucroLiquidoPercentualAnual, state='disabled',
                                        width=12)  # , font=mono_font_IRPF)
    entIRPFRetidoAnual = Entry(frameIRPFAnual, textvariable=txtIRPFRetidoFonteAnual, state='disabled',
                            width=12)  # , font=mono_font_IRPF)
    entImpostosDevidosAnual = Entry(frameIRPFAnual, textvariable=txtImpostosDevidosAnual, state='disabled',
                                 width=12)  # , font=mono_font_IRPF)

    ToolTip.CreateToolTip(labelLucroLiquidoAnual, text="Lucro Bruto - Despesas - Impostos. \n"
                                                    "No programa de IRPF, lançar este valor em\n"
                                                    "Rendimentos Isentos e Não Tributáveis, opção 20.\n"
                                                       "Desconsidera os lucros obtidos em meses em que\n"
                                                       "se pagou imposto de renda (já lançados nos meses \n"
                                                       "específicos em que se recolheu IR)")


    btnCalculaIRPFAnual = Button(frameIRPFBoth,
                                  text="Calcula IRPF Anual")  # , font=mono_font)
    btnCalculaIRPFAnual.grid(row=3, column=0, columnspan=2, sticky='nesw')
    ############################### Arranjo dos WIdgets###########################################
    labelVendasAnual.grid(row=1, column=0, sticky='e')
    labelLucroBrutoAnual.grid(row=2, column=0, sticky='e')
    labelDespesasMensaisAnual.grid(row=3, column=0, sticky='e')
    labelLucroLiquidoAnual.grid(row=4, column=0, sticky='e')
    labelLucroLiquidoPercentualAnual.grid(row=5, column=0, sticky='e')
    labelIRPFRetidoAnual.grid(row=6, column=0, sticky='e')
    labelImpostosDevidosAnual.grid(row=7, column=0, sticky='e')
    entVendasAnual.grid(row=1, column=1, sticky='nesw')
    entLucroBrutoAnual.grid(row=2, column=1, sticky='nesw')
    entDespesasMensaisAnual.grid(row=3, column=1, sticky='nesw')
    entLucroLiquidoAnual.grid(row=4, column=1, sticky='nesw')
    entLucroLiquidoPercentualAnual.grid(row=5, column=1, sticky='nesw')
    entIRPFRetidoAnual.grid(row=6, column=1, sticky='nesw')
    entImpostosDevidosAnual.grid(row=7, column=1, sticky='nesw')
    # Os frames abaixo estão linkados no frameIRPFBoth
    frameIRPFAnual.grid(row=2, column=0, columnspan=2, sticky='nesw')
    frameIRPFAnual.columnconfigure(0, weight=1)
    ##############################################################################################
    ##############################Fim Frame IRPF Anual - frameIRPFAnual###########################
    ##############################################################################################










    ##############################################################################################
    #################################Frame Grafico Pie - framePie#################################
    ##############################################################################################
    framePie = LabelFrame(window, text='')  # "Controles Posição Consolidada")
    labels = ['0']  # , 'b', 'c', 'd']
    sizes = ['0']  # 20, 30, 50]
    fig = plt.figure(4, figsize=(6.5, 4.8))
    ax1 = fig.add_subplot(111)
    ax1.set_title("Posição Consolidada")
    ax1.axis("equal")
    pie = ax1.pie(sizes, labels=labels, startangle=0)
    canvasCarteiraPie = FigureCanvasTkAgg(fig, master=framePie)
    canvasCarteiraPie.draw()
    # creating the Matplotlib toolbar
    toolbarPie = NavigationToolbar2Tk(canvasCarteiraPie, framePie)
    toolbarPie.update()
    btnUpdatePie = Button(framePie, text="Refresh")
    # Criando Progress Bar
    progressPIE = ttk.Progressbar(framePie, orient=HORIZONTAL,
                                  length=150, mode='indeterminate')
    ############################### Arranjo dos WIdgets###########################################
    toolbarPie.grid(row=1, column=0, sticky=W)
    btnUpdatePie.grid(row=1, column=1, sticky=E)
    progressPIE.grid(row=0, column=0, sticky='nesw', columnspan=2, padx=250, pady=250)
    canvasCarteiraPie.get_tk_widget().grid(row=0, column=0, columnspan=2, sticky='nesw')  # , ipadx=40, ipady=20)
    ##############################################################################################
    ##############################Fim Frame GraficoPie - framePie##############################
    ##############################################################################################





    ##############################################################################################
    ##########################Frame Grafico Desempenho - frameDesempenho##########################
    ##############################################################################################
    frameDesempenho = LabelFrame(window, text='')  # "Controles Desempenho")
    plt.style.use('seaborn-whitegrid')
    # labelsDesempenho = ['a']#, 'b', 'c', 'd']
    # sizesDesempenho = [0]#, 20, 30, 50]
    # sizesIbov = [3, 10, 15, 20]
    figDesempenho = plt.figure(5, figsize=(6.8, 4.8))
    ax1Desempenho = figDesempenho.add_subplot(111)
    ax1Desempenho.set_title("Desempenho")
    linhaDesempenho = ax1Desempenho.plot()  # labelsDesempenho, sizesDesempenho)
    canvasDesempenho = FigureCanvasTkAgg(figDesempenho, master=frameDesempenho)
    canvasDesempenho.draw()
    # creating the Matplotlib toolbar
    toolbarDesempenho = NavigationToolbar2Tk(canvasDesempenho, frameDesempenho)
    varIbov = IntVar()
    varPapeis = IntVar()
    varCarteira = IntVar()
    chkBoxesFrame = LabelFrame(frameDesempenho, text='')
    chkBoxIbov = Checkbutton(chkBoxesFrame,
                             text="Ibov",
                             variable=varIbov).grid(row=0, column=0, sticky=W)
    chkBoxPapeis = Checkbutton(chkBoxesFrame,
                               text="Papéis",
                               variable=varPapeis).grid(row=0, column=1, sticky=W)
    chkBoxCarteira = Checkbutton(chkBoxesFrame,
                                 text="Carteira",
                                 variable=varCarteira).grid(row=0, column=2, sticky=W)
    btnUpdateDesempenho = Button(frameDesempenho,
                                 text="Refresh")
    toolbarDesempenho.update()
    #Criando a Progress Bar
    progressDesempenho = ttk.Progressbar(frameDesempenho, orient=HORIZONTAL,
                                         length=150, mode='indeterminate')
    ############################### Arranjo dos WIdgets###########################################
    toolbarDesempenho.grid(row=1, column=0, sticky=W)
    chkBoxesFrame.grid(row=1, column=1, sticky=E)
    btnUpdateDesempenho.grid(row=1, column=2, sticky=E)
    progressDesempenho.grid(row=0, column=0, sticky='nesw', columnspan=3, padx=250, pady=250)
    canvasDesempenho.get_tk_widget().grid(row=0, column=0, columnspan=3, stick='nesw')
    ##############################################################################################
    ######################Fim Frame Grafico Desempenho - frameDesempenho##########################
    ##############################################################################################











    frameIndicadores = LabelFrame(window, text="Indicadores", padx=5, pady=5)  # , font=mono_font_Indicadores, )
    ##############################################################################################
    #####################Frame Indicadores Tecnicos - frameIndTec#################################
    ##############################################################################################
    #frameIndTec = LabelFrame(frameIndicadores, text="Indicadores Técnicos", padx=5, pady=5)  # , font=mono_font_Indicadores, )
    textAreaIndicators = Text(frameIndicadores, width=50, height=12)  # , font=mono_font_Indicadores)
    ############################### Arranjo dos WIdgets###########################################
    textAreaIndicators.grid(row=0, column=0, stick='nw')#, rowspan=9, columnspan=1, stick=W)
    ##############################################################################################
    ####################Fim Frame Indicadores Tecnicos - frameIndTec##############################
    ##############################################################################################

    ##############################################################################################
    #####################Frame Indicadores Tecnicos - frameIndFund################################
    ##############################################################################################
    #frameIndFund = LabelFrame(frameIndicadores, text="Fundamentos", padx=5, pady=5)  # , font=mono_font_Indicadores)
    textAreaIndicatorsFund = Text(frameIndicadores, width=50, height=10)  # , font=mono_font_Indicadores)
    ############################### Arranjo dos WIdgets###########################################
    textAreaIndicatorsFund.grid(row=1, column=0, stick='sw')#, rowspan=6, columnspan=1, stick=W)
    ##############################################################################################
    ####################Fim Frame Indicadores Tecnicos - frameIndFund#############################
    ##############################################################################################




























    ##############################################################################################
    #################################Frames Alignment#############################################
    ##############################################################################################
    frameButoes.grid(row=0, column=0) #, columnspan=2, rowspan=1)  # , sticky='nesw')
    frameList.grid(row=0, column=1) #, rowspan=2, columnspan=2, sticky=E)#, columnspan=1)
    #frameIndTec.grid(row=0, column=2, stick=NW)
    #frameIndFund.grid(row=0, column=2, rowspan=2, stick='ne')
    frameIndicadores.grid(row=0, column=2, stick='nesw')
    frameIRPFBoth.grid(row=1, column=2)#, sticky="nesw")
    framePie.grid(row=1, column=0)  # , columnspan=3, stick=SW)
    frameDesempenho.grid(row=1, column=1)  # , columnspan=6, stick=SW)




    #############################################################################################
    ################################Frames Alignment#############################################
    #############################################################################################









    #Adicionando um pouco de SWAG a interface...
    for child in window.winfo_children():
        widget_class = child.__class__.__name__
        if widget_class == "Button":
            child.grid_configure(sticky='WE', padx=x_pad, pady=y_pad)
        elif widget_class == "Listbox":
            child.grid_configure(padx=0, pady=0, sticky='NS')
        elif widget_class == "Scrollbar":
            child.grid_configure(padx=0, pady=0, sticky='NS')
        elif widget_class == "Label" or widget_class == "Entry":
            child.grid_configure(padx=x_pad, pady=y_pad, sticky='N')

    def run(self):
        Gui.window.mainloop()

