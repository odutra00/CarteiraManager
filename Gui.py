from tkinter import *
from tkinter import ttk
import tkfontchooser
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
    window.geometry('1920x990')
    mono_font = tkfontchooser.Font(family="Arial", size=18)
    mono_font_IRPF = tkfontchooser.Font(family="Arial", size=16)
    mono_font_Indicadores = tkfontchooser.Font(family="Arial", size=15)

    #Criando Menus
    menubar = Menu(window)
    filemenu = Menu(menubar, tearoff=0)
    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=filemenu)
    menubar.add_cascade(label="Help", menu=helpmenu)
    window.config(menu=menubar)

    #Criando variáveis que armazenarão o texto inserido pelo usuário...
    txtMercado      = StringVar()
    txtPapel        = StringVar()
    txtStatus       = StringVar()
    txtData         = StringVar()
    txtValorCompra  = StringVar()
    txtQuantidade   = StringVar()
    txtCustos       = StringVar()
    varBusca        = IntVar()

    txtLabelFrame = StringVar()
    txtMercadoIRPF = StringVar()
    txtVendas = StringVar()
    txtLucroBruto = StringVar()
    txtLucroLiquido = StringVar()
    txtLucroLiquidoPercentual = StringVar()
    txtImpostosDevidos = StringVar()
    txtIRPFRetidoFonte = StringVar()
    txtDespesasMensais = StringVar()

    txtMercadoIRPFDT = StringVar()
    txtVendasDT = StringVar()
    txtLucroBrutoDT = StringVar()
    txtLucroLiquidoDT = StringVar()
    txtLucroLiquidoPercentualDT = StringVar()
    txtImpostosDevidosDT = StringVar()
    txtIRPFRetidoFonteDT = StringVar()
    txtDespesasMensaisDT = StringVar()

    txtPL = StringVar()
    frameButoes = LabelFrame(window, text="Controles")

    #Criando os objetos que estarão na janela...
    lblMercado      = Label(frameButoes, text="Mercado", font=mono_font)
    lblPapel        = Label(frameButoes, text="Ação", font=mono_font)
    lblStatus       = Label(frameButoes, text="Status", font=mono_font)
    lblData         = Label(frameButoes, text="Data", font=mono_font)
    lblValorCompra  = Label(frameButoes, text="Valor", font=mono_font)
    lblQuantidade   = Label(frameButoes, text="Quantidade", font=mono_font)
    lblCustos       = Label(frameButoes, text="Custos", font=mono_font)

    #Criando campos de Input
    #entMercado      = Entry(window, textvariable=txtMercado)
    comboMercado = ttk.Combobox(frameButoes, values=[
                                        "Vista",
                                        "Opções"],
                                    state="Vista",
                                    textvariable=txtMercado,
                                    font=mono_font)
    entPapel        = Entry(frameButoes,
                            textvariable=txtPapel,
                            font=mono_font)
    #entStatus       = Entry(window, textvariable=txtStatus)
    comboStatus = ttk.Combobox(frameButoes, values=[
                                        "Compra",
                                        "Venda"],
                               state="Compra",
                               textvariable=txtStatus,
                               font=mono_font)
    entData         = Entry(frameButoes, textvariable=txtData, font=mono_font)
    entValor        = Entry(frameButoes, textvariable=txtValorCompra, font=mono_font)
    entQuantidade   = Entry(frameButoes, textvariable=txtQuantidade, font=mono_font)
    entCustos       = Entry(frameButoes, textvariable=txtCustos, font=mono_font)




    #Criando ListBox e ScrollBar
    frameList = LabelFrame(window, text='')#"Labels das colunas e a lista e a scroll bar
    labelsColunas = Label(frameList,
                          text="   MKT\t Papel\t Status\t        Data         Preço        PM          N        NC     Custos",
                          font=mono_font)
    #For windows
    # labelsColunas = Label(frameList,
    #                       text="   MKT   Papel    Status         Data         Preço      PM        N     NC    Custos",
    #                       font=mono_font)
    listPapels   = Listbox(frameList, width=70, height=14, font=mono_font)
    scrollPapelsY = Scrollbar(frameList)
    #scrollPapelsX = Scrollbar(frameList)
    labelsColunas.grid(row=0, column=0, columnspan=2, sticky=W)
    listPapels.grid(row=1, column=0, rowspan=9, sticky='nesw')
    scrollPapelsY.grid(row=1, column=1, rowspan=9, sticky='nes')
    #scrollPapelsX.grid(row=10, column=1, rowspan=9, sticky='nesw')

    #Criando Botoes
    btnViewAll     = Button(frameButoes, text="Ver todos", font=mono_font)
    btnBuscar      = Button(frameButoes, text="Buscar", font=mono_font)
    btnInserir     = Button(frameButoes, text="Inserir", font=mono_font)
    #btnUpdate      = Button(frameButoes, text="Atualizar Selecionado", font=mono_font)
    btnDel         = Button(frameButoes, text="Deletar Selecionado", font=mono_font)
    btnClose       = Button(frameButoes, text="Fechar", font=mono_font)

    #Criando Message Box
    #About = messagebox.showinfo(title=None, message=None, **options)¶

    #Criando a região do Plot PIE Posição Consolidada
    framePie = LabelFrame(window, text='')#"Controles Posição Consolidada")
    labels = ['0']#, 'b', 'c', 'd']
    sizes = ['0']# 20, 30, 50]
    fig = plt.figure(4, figsize=(6.5, 4.8))
    ax1 = fig.add_subplot(111)
    ax1.set_title("Posição Consolidada")
    ax1.axis("equal")
    pie = ax1.pie(sizes, labels=labels, startangle=0)
    canvasCarteiraPie = FigureCanvasTkAgg(fig, master=window)
    canvasCarteiraPie.draw()
    # creating the Matplotlib toolbar
    toolbarPie = NavigationToolbar2Tk(canvasCarteiraPie, framePie)
    toolbarPie.grid(row=0, column=0, sticky=W)
    toolbarPie.update()

    btnUpdatePie = Button(framePie, text="Refresh")
    btnUpdatePie.grid(row=0, column=1, sticky=W)


    #Criando Regiao para comparaçao desempenho
    frameDesempenho = LabelFrame(window, text='')#"Controles Desempenho")
    plt.style.use('seaborn-whitegrid')
    #labelsDesempenho = ['a']#, 'b', 'c', 'd']
    #sizesDesempenho = [0]#, 20, 30, 50]
    #sizesIbov = [3, 10, 15, 20]
    figDesempenho = plt.figure(5, figsize=(6.8, 4.8))
    ax1Desempenho = figDesempenho.add_subplot(111)
    ax1Desempenho.set_title("Desempenho")
    linhaDesempenho = ax1Desempenho.plot()#labelsDesempenho, sizesDesempenho)
    canvasDesempenho = FigureCanvasTkAgg(figDesempenho, master=window)
    canvasDesempenho.draw()
    # creating the Matplotlib toolbar
    toolbarDesempenho = NavigationToolbar2Tk(canvasDesempenho, frameDesempenho)
    toolbarDesempenho.grid(row=0, column=0, sticky=W)

    varIbov = IntVar()
    varPapeis = IntVar()
    varCarteira = IntVar()
    chkBoxIbov = Checkbutton(frameDesempenho,
                             text="Ibov",
                             variable=varIbov).grid(row=0, column=1, sticky=W)
    chkBoxPapeis = Checkbutton(frameDesempenho,
                               text="Papéis",
                               variable=varPapeis).grid(row=0, column=2, sticky=W)
    chkBoxCarteira = Checkbutton(frameDesempenho,
                                 text="Carteira",
                                 variable=varCarteira).grid(row=0, column=3, sticky=W)
    btnUpdateDesempenho = Button(frameDesempenho,
                             text="Refresh")
    btnUpdateDesempenho.grid(row=0, column=4, sticky=W)

    toolbarDesempenho.update()











    # Frame to Exbit both IRPF Day-Trade and regular for the chosen month
    txtLabelFrameBoth = "IRPF Mensal"
    frameIRPFBoth = LabelFrame(window, text=txtLabelFrameBoth, padx=5, pady=10, font=mono_font_IRPF)
    btnCalculaIRPFMensal = Button(frameIRPFBoth,
                                  text="Calcula IRPF Mensal",
                                  font=mono_font)
    btnCalculaIRPFMensal.grid(row=1, column=0, columnspan=2, sticky='nesw')









    #Frame to Exbit due IRPF Regular for the chosen month
    txtLabelFrame = "IRPF Regular Mensal"
    frameIRPF = LabelFrame(frameIRPFBoth, text=txtLabelFrame, width=5)#, padx=20, pady=20)
    labelMercado = Label(frameIRPF, text="Mercado", font=mono_font_IRPF)
    labelVendas = Label(frameIRPF, text="Vendas", font=mono_font_IRPF)
    labelLucroBruto = Label(frameIRPF, text="L. Bruto", font=mono_font_IRPF)
    labelDespesasMensais = Label(frameIRPF, text="Despesas", font=mono_font_IRPF)
    labelLucroLiquido = Label(frameIRPF, text="L. Líquido", font=mono_font_IRPF)
    labelLucroLiquidoPercentual = Label(frameIRPF, text="L. Líquido %", font=mono_font_IRPF)
    labelIRPFRetido = Label(frameIRPF, text="IRPF Retido", font=mono_font_IRPF)
    labelImpostosDevidos = Label(frameIRPF, text="IRPF Devido", font=mono_font_IRPF)

    #entMercadoIRPF = Entry(frameIRPF, textvariable=txtMercadoIRPF, state='disabled', width=2)
    entVendas = Entry(frameIRPF, textvariable=txtVendas, state='disabled', width=12, font=mono_font_IRPF)
    entLucroBruto = Entry(frameIRPF, textvariable=txtLucroBruto, state='disabled', width=12, font=mono_font_IRPF)
    entDespesasMensais = Entry(frameIRPF, textvariable=txtDespesasMensais, state='disabled', width=12, font=mono_font_IRPF)
    entLucroLiquido = Entry(frameIRPF, textvariable=txtLucroLiquido, state='disabled', width=12, font=mono_font_IRPF)
    entLucroLiquidoPercentual = Entry(frameIRPF, textvariable=txtLucroLiquidoPercentual, state='disabled', width=12, font=mono_font_IRPF)
    entIRPFRetido = Entry(frameIRPF, textvariable=txtIRPFRetidoFonte, state='disabled', width=12, font=mono_font_IRPF)
    entImpostosDevidos = Entry(frameIRPF, textvariable=txtImpostosDevidos, state='disabled', width=12, font=mono_font_IRPF)


    ToolTip.CreateToolTip (labelLucroBruto, text = "Lucro antes de descontar \n"
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

    #Posicionamento dos labels IRPF dentro do frameIRPF
    #cal.grid(row=0, column=0, columnspan=2)
    #labelMercado.grid(row=1, column=0, stick=E)
    labelVendas.grid(row=1, column=0, sticky='nesw')
    labelLucroBruto.grid(row=2, column=0, sticky='nesw')
    labelDespesasMensais.grid(row=3, column=0, sticky='nesw')
    labelLucroLiquido.grid(row=4, column=0, sticky='nesw')
    labelLucroLiquidoPercentual.grid(row=5, column=0, sticky='nesw')
    labelIRPFRetido.grid(row=6, column=0, sticky='nesw')
    labelImpostosDevidos.grid(row=7, column=0, sticky='nesw')

    #entMercadoIRPF.grid(row=1, column=1)
    entVendas.grid(row=1, column=1, sticky='nesw')
    entLucroBruto.grid(row=2, column=1, sticky='nesw')
    entDespesasMensais.grid(row=3, column=1, sticky='nesw')
    entLucroLiquido.grid(row=4, column=1, sticky='nesw')
    entLucroLiquidoPercentual.grid(row=5, column=1, sticky='nesw')
    entIRPFRetido.grid(row=6, column=1, sticky='nesw')
    entImpostosDevidos.grid(row=7, column=1, sticky='nesw')

    frameIRPF.grid(row=0, column=0, sticky='nesw')
    frameIRPF.columnconfigure(0, weight=1)
















    # Frame to Exbit due IRPF Day-Trade for the chosen month
    txtLabelFrameDayTrade = "IRPF DayTrade Mensal"
    frameIRPFDayTrade = LabelFrame(frameIRPFBoth, text=txtLabelFrameDayTrade)#, padx=20, pady=20)

    labelMercadoDT = Label(frameIRPFDayTrade, text="Mercado", font=mono_font_IRPF)
    labelVendasDT = Label(frameIRPFDayTrade, text="Vendas", font=mono_font_IRPF)
    labelLucroBrutoDT = Label(frameIRPFDayTrade, text="L. Bruto", font=mono_font_IRPF)
    labelDespesasMensaisDT = Label(frameIRPFDayTrade, text="Despesas", font=mono_font_IRPF)
    labelLucroLiquidoDT = Label(frameIRPFDayTrade, text="L. Líquido", font=mono_font_IRPF)
    labelLucroLiquidoPercentualDT = Label(frameIRPFDayTrade, text="L. Líquido %", font=mono_font_IRPF)
    labelIRPFRetidoDT = Label(frameIRPFDayTrade, text="IRPF Retido", font=mono_font_IRPF)
    labelImpostosDevidosDT = Label(frameIRPFDayTrade, text="IRPF Devido", font=mono_font_IRPF)

    entMercadoIRPFDT = Entry(frameIRPFDayTrade, textvariable=txtMercadoIRPFDT, state='disabled', width=12, font=mono_font_IRPF)
    entVendasDT = Entry(frameIRPFDayTrade, textvariable=txtVendasDT, state='disabled', width=12, font=mono_font_IRPF)
    entLucroBrutoDT = Entry(frameIRPFDayTrade, textvariable=txtLucroBrutoDT, state='disabled', width=12, font=mono_font_IRPF)
    entDespesasMensaisDT = Entry(frameIRPFDayTrade, textvariable=txtDespesasMensaisDT, state='disabled', width=12, font=mono_font_IRPF)
    entLucroLiquidoDT = Entry(frameIRPFDayTrade, textvariable=txtLucroLiquidoDT, state='disabled', width=12, font=mono_font_IRPF)
    entLucroLiquidoPercentualDT = Entry(frameIRPFDayTrade, textvariable=txtLucroLiquidoPercentualDT, state='disabled', width=12, font=mono_font_IRPF)
    entIRPFRetidoDT = Entry(frameIRPFDayTrade, textvariable=txtIRPFRetidoFonteDT, state='disabled', width=12, font=mono_font_IRPF)
    entImpostosDevidosDT = Entry(frameIRPFDayTrade, textvariable=txtImpostosDevidosDT, state='disabled', width=12, font=mono_font_IRPF)


    labelVendasDT.grid(row=1, column=0, sticky='nesw')
    labelLucroBrutoDT.grid(row=2, column=0, sticky='nesw')
    labelDespesasMensaisDT.grid(row=3, column=0, sticky='nesw')
    labelLucroLiquidoDT.grid(row=4, column=0, sticky='nesw')
    labelLucroLiquidoPercentualDT.grid(row=5, column=0, sticky='nesw')
    labelIRPFRetidoDT.grid(row=6, column=0, sticky='nesw')
    labelImpostosDevidosDT.grid(row=7, column=0, sticky='nesw')

    # entMercadoIRPF.grid(row=1, column=1)
    entVendasDT.grid(row=1, column=1, sticky='nesw')
    entLucroBrutoDT.grid(row=2, column=1, sticky='nesw')
    entDespesasMensaisDT.grid(row=3, column=1, sticky='nesw')
    entLucroLiquidoDT.grid(row=4, column=1, sticky='nesw')
    entLucroLiquidoPercentualDT.grid(row=5, column=1, sticky='nesw')
    entIRPFRetidoDT.grid(row=6, column=1, sticky='nesw')
    entImpostosDevidosDT.grid(row=7, column=1, sticky='nesw')

    frameIRPFDayTrade.grid(row=0, column=1, sticky='nesw')
    frameIRPFDayTrade.columnconfigure(0, weight=1)














    #Frame to Exbit indicadores tecnicos
    frameIndTec = LabelFrame(window, text="Indicadores Técnicos",
                             font=mono_font_Indicadores, padx=5, pady=5)
    #Labels
    #labelPL = Label(frameIndTec, text="P/L = ")
    #Entries
    #entPL = Entry(frameIndTec, textvariable=txtPL, state='disabled')
    #Caixa de Texto
    textAreaIndicators = Text(frameIndTec, width=50, height=12, font=mono_font_Indicadores)
    #Grid Indicadores Tecnicos dentro do frame
    #labelPL.grid(row=0, column=0, stick=W)
    #entPL.grid(row=0, column=1, stick=W)
    textAreaIndicators.grid(row=0, column=0, rowspan=9, columnspan=1, stick=W)


    #Frame to Exbit Fundamentos
    frameIndFund = LabelFrame(window, text="Informações",
                              font=mono_font_Indicadores, padx=5, pady=5)
    #Caixa de Texto
    textAreaIndicatorsFund = Text(frameIndFund, width=50, height=10, font=mono_font_Indicadores)
    textAreaIndicatorsFund.grid(row=0, column=0, rowspan=6, columnspan=1, stick=W)







    #Frame Controles
    #Associando os objetos a grid do frame
    lblMercado.grid(row=0, column=0, sticky=E)
    lblStatus.grid(row=1, column=0, sticky=E)
    lblPapel.grid(row=2, column=0, sticky=E)
    lblData.grid(row=3, column=0, sticky=E)
    lblValorCompra.grid(row=4, column=0, sticky=E)
    lblQuantidade.grid(row=5, column=0, sticky=E)
    lblCustos.grid(row=6, column=0, sticky=E)

    #entMercado.grid(row=0, column=1, padx=20, pady=50)
    comboMercado.grid(row=0, column=1)#, padx=10, pady=50)
    comboStatus.grid(row=1, column=1)
    entPapel.grid(row=2, column=1)
    #entStatus.grid(row=2, column=1)
    entData.grid(row=3, column=1)
    entValor.grid(row=4, column=1)
    entQuantidade.grid(row=5, column=1)
    entCustos.grid(row=6, column=1)

    btnViewAll.grid(row=7, column=0, columnspan=2, sticky='nesw')  # 7
    btnBuscar.grid(row=8, column=0, columnspan=2, sticky='nesw')
    btnInserir.grid(row=9, column=0, columnspan=2, sticky='nesw')
    #btnUpdate.grid(row=10, column=0, columnspan=2, sticky='nesw')
    btnDel.grid(row=11, column=0, columnspan=2, sticky='nesw')









    #Lista de exibição de ativos e scroo bar
    #listPapels.grid(row=0, column=2, rowspan=9, columnspan=4, sticky=E)#, columnspan=1)
    #scrollPapelsY.grid(row=0, column=6, rowspan=9, sticky=E)








    #Canvas Alignment
    canvasCarteiraPie.get_tk_widget().grid(row=9, column=0, columnspan=3, stick=NW)  # , ipadx=40, ipady=20)
    framePie.grid(row=10, column=0, columnspan=3, stick=SW)
    canvasDesempenho.get_tk_widget().grid(row=9, column=3, columnspan=5, stick=NW)
    frameDesempenho.grid(row=10, column=3, columnspan=6, stick=SW)

    #Frames Alignment
    frameButoes.grid(row=0, column=0, columnspan=2, rowspan=9)  # , sticky='nesw')
    frameIndTec.grid(row=0, column=7, rowspan=8, stick=NW)
    frameIndFund.grid(row=7, column=7, rowspan=3, stick=NW)
    frameIRPFBoth.grid(row=9, column=7, columnspan=1, sticky='sw')
    frameList.grid(row=0, column=2, rowspan=9, columnspan=4, sticky=E)#, columnspan=1)


    #Associando a Scrollbar com a Listbox...
    listPapels.configure(yscrollcommand=scrollPapelsY.set)#, xscrollcommand=scrollPapelsX.set)
    scrollPapelsY.configure(command=listPapels.yview)
    #scrollPapelsX.configure(command=listPapels.xview)

    # Criando Progress Bar
    progressPIE = ttk.Progressbar(window, orient=HORIZONTAL,
                               length=150, mode='indeterminate')
    progressDesempenho = ttk.Progressbar(window, orient=HORIZONTAL,
                               length=150, mode='indeterminate')

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

