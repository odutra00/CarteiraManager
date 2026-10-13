from datetime import datetime
from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.database import Database
from core.models import ResumoAnualIRPF, ResumoIRPF
from core.tax_service import TaxService


class ReadOnlyField(QLineEdit):
    """Campo somente leitura com estilo visual limpo para resultados fiscais."""

    def __init__(self, value: str = "R$ 0,00", tooltip: str = ""):
        super().__init__(value)
        self.setReadOnly(True)
        self.setToolTip(tooltip)
        self.setStyleSheet(
            """
            ReadOnlyField {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                color: #ffffff;
            }
            """
        )


class TaxTab(QWidget):
    """Aba de Apuração de IRPF (Swing Trade, Day Trade e Consolidação Anual)."""

    def __init__(self, db: Database, tax_service: TaxService, parent=None):
        super().__init__(parent)
        self.db = db
        self.tax_service = tax_service

        self._init_ui()
        self.calculate()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Barra Superior de Controles (Mês / Ano / Calcular)
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Mês de Apuração:"))

        self.cb_mes = QComboBox()
        meses = [
            "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril",
            "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto",
            "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"
        ]
        self.cb_mes.addItems(meses)
        self.cb_mes.setCurrentIndex(datetime.now().month - 1)
        controls_layout.addWidget(self.cb_mes)

        controls_layout.addWidget(QLabel("Ano:"))
        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2000, 2099)
        self.spin_ano.setValue(datetime.now().year)
        controls_layout.addWidget(self.spin_ano)

        self.btn_calcular = QPushButton("Calcular IRPF")
        self.btn_calcular.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold; padding: 6px 15px;")
        self.btn_calcular.clicked.connect(self.calculate)
        controls_layout.addWidget(self.btn_calcular)
        controls_layout.addStretch()

        main_layout.addLayout(controls_layout)

        # Área rolável com os cards de apuração
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QGridLayout(scroll_content)
        scroll_layout.setSpacing(15)

        # 1. Card Swing Trade (Operações Comuns)
        group_swing = QGroupBox("IRPF Mensal - Operações Comuns (Swing Trade)")
        form_swing = QFormLayout(group_swing)
        form_swing.setSpacing(8)

        self.f_st_vendas = ReadOnlyField("R$ 0,00", "Volume total financeiro alienado (vendido) no mês.")
        self.f_st_bruto = ReadOnlyField("R$ 0,00", "Lucro antes das despesas (Venda - Preço Médio).")
        self.f_st_despesas = ReadOnlyField("R$ 0,00", "Custos operacionais (corretagem, emolumentos, taxas B3).")
        self.f_st_liquido = ReadOnlyField("R$ 0,00", "Lucro Bruto menos Despesas operacionais.")
        self.f_st_isento = ReadOnlyField("NÃO", "Vendas de ações até R$ 20.000 no mês são isentas.")
        self.f_st_prej_ant = ReadOnlyField("R$ 0,00", "Prejuízos acumulados de meses anteriores a compensar.")
        self.f_st_base = ReadOnlyField("R$ 0,00", "Base de cálculo líquida tributável após compensação.")
        self.f_st_irrf = ReadOnlyField("R$ 0,00", "IRRF retido na fonte (0,005% da venda se > R$ 1,00).")
        self.f_st_devido = ReadOnlyField("R$ 0,00", "Imposto bruto apurado à alíquota de 15%.")
        self.f_st_pagar = ReadOnlyField("R$ 0,00", "Valor da DARF a recolher (Código 6015) até o último dia útil do mês seguinte.")
        self.f_st_prej_fim = ReadOnlyField("R$ 0,00", "Saldo restante de prejuízos a compensar nos próximos meses.")

        form_swing.addRow("Total de Vendas:", self.f_st_vendas)
        form_swing.addRow("Lucro Bruto:", self.f_st_bruto)
        form_swing.addRow("Despesas Operacionais:", self.f_st_despesas)
        form_swing.addRow("Lucro Líquido:", self.f_st_liquido)
        form_swing.addRow("Status de Isenção (<= 20k):", self.f_st_isento)
        form_swing.addRow("Prejuízo Anterior a Compensar:", self.f_st_prej_ant)
        form_swing.addRow("Base de Cálculo Tributável:", self.f_st_base)
        form_swing.addRow("IRRF Dedo-Duro (0,005%):", self.f_st_irrf)
        form_swing.addRow("Imposto Devido (15%):", self.f_st_devido)
        form_swing.addRow("DARF a Pagar:", self.f_st_pagar)
        form_swing.addRow("Prejuízo a Compensar Restante:", self.f_st_prej_fim)

        scroll_layout.addWidget(group_swing, 0, 0)

        # 2. Card Day Trade
        group_dt = QGroupBox("IRPF Mensal - Day Trade")
        form_dt = QFormLayout(group_dt)
        form_dt.setSpacing(8)

        self.f_dt_vendas = ReadOnlyField("R$ 0,00", "Volume total financeiro alienado em Day Trade.")
        self.f_dt_bruto = ReadOnlyField("R$ 0,00", "Lucro bruto de operações intraday.")
        self.f_dt_despesas = ReadOnlyField("R$ 0,00", "Taxas e corretagens de Day Trade.")
        self.f_dt_liquido = ReadOnlyField("R$ 0,00", "Lucro líquido apurado no mês.")
        self.f_dt_prej_ant = ReadOnlyField("R$ 0,00", "Prejuízos acumulados anteriores de Day Trade.")
        self.f_dt_base = ReadOnlyField("R$ 0,00", "Base de cálculo tributável de Day Trade.")
        self.f_dt_irrf = ReadOnlyField("R$ 0,00", "IRRF retido na fonte pela corretora (1% do rendimento).")
        self.f_dt_devido = ReadOnlyField("R$ 0,00", "Imposto apurado à alíquota de 20%.")
        self.f_dt_pagar = ReadOnlyField("R$ 0,00", "DARF a recolher de Day Trade (Código 6015).")
        self.f_dt_prej_fim = ReadOnlyField("R$ 0,00", "Saldo restante de prejuízos de Day Trade a compensar.")

        form_dt.addRow("Total de Vendas:", self.f_dt_vendas)
        form_dt.addRow("Lucro Bruto:", self.f_dt_bruto)
        form_dt.addRow("Despesas Operacionais:", self.f_dt_despesas)
        form_dt.addRow("Lucro Líquido:", self.f_dt_liquido)
        form_dt.addRow("Prejuízo Anterior a Compensar:", self.f_dt_prej_ant)
        form_dt.addRow("Base de Cálculo Tributável:", self.f_dt_base)
        form_dt.addRow("IRRF Retido (1%):", self.f_dt_irrf)
        form_dt.addRow("Imposto Devido (20%):", self.f_dt_devido)
        form_dt.addRow("DARF a Pagar:", self.f_dt_pagar)
        form_dt.addRow("Prejuízo Day Trade Restante:", self.f_dt_prej_fim)

        scroll_layout.addWidget(group_dt, 0, 1)

        # 3. Card Declaração Anual (DIRPF)
        group_anual = QGroupBox("Declaração Anual do IRPF (DIRPF - Acumulado no Ano)")
        form_anual = QFormLayout(group_anual)
        form_anual.setSpacing(8)

        self.f_anual_isento = ReadOnlyField(
            "R$ 0,00",
            "Lançar em 'Rendimentos Isentos e Não Tributáveis', Código 20:\n"
            "Ganhos líquidos em operações no mercado à vista de ações negociadas em bolsa com vendas até R$ 20.000.",
        )
        self.f_anual_tributavel = ReadOnlyField(
            "R$ 0,00",
            "Lançar mês a mês na aba 'Renda Variável' do programa IRPF.",
        )
        self.f_anual_irrf = ReadOnlyField(
            "R$ 0,00",
            "Lançar no campo 'Imposto Retido na Fonte (Lei 11.033/2004)' para abater do imposto anual.",
        )
        self.f_anual_pago = ReadOnlyField(
            "R$ 0,00",
            "Lançar no campo 'Imposto Pago' na aba Renda Variável para cada mês.",
        )
        self.f_anual_prej = ReadOnlyField(
            "R$ 0,00",
            "Saldo de prejuízo acumulado a transportar para o ano-calendário seguinte.",
        )

        form_anual.addRow("Rendimentos Isentos (Vendas <= 20k):", self.f_anual_isento)
        form_anual.addRow("Ganhos Líquidos Tributáveis:", self.f_anual_tributavel)
        form_anual.addRow("Total IRRF Dedo-Duro Retido no Ano:", self.f_anual_irrf)
        form_anual.addRow("Total Imposto Pago via DARF:", self.f_anual_pago)
        form_anual.addRow("Prejuízo a Compensar p/ Próximo Ano:", self.f_anual_prej)

        scroll_layout.addWidget(group_anual, 1, 0, 1, 2)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def calculate(self):
        """Calcula os impostos do mês e ano selecionados com compensação contínua de prejuízos."""
        mes = self.cb_mes.currentIndex() + 1
        ano = self.spin_ano.value()

        # Para apurar o mês selecionado com prejuízo histórico correto,
        # calculamos mês a mês do início do ano até o mês alvo
        losses = {"swing": 0.0, "day_trade": 0.0}
        res_swing = None
        res_dt = None

        for m in range(1, mes + 1):
            res_swing, res_dt, losses = self.tax_service.calculate_month(ano, m, carryover_losses=losses)

        if res_swing:
            self.f_st_vendas.setText(f"R$ {res_swing.total_vendas:,.2f}")
            self.f_st_bruto.setText(f"R$ {res_swing.lucro_bruto:,.2f}")
            self.f_st_despesas.setText(f"R$ {res_swing.despesas:,.2f}")
            self.f_st_liquido.setText(f"R$ {res_swing.lucro_liquido_mes:,.2f}")
            self.f_st_isento.setText("SIM (ISENTO)" if res_swing.isento else "NÃO (TRIBUTÁVEL)")
            self.f_st_prej_ant.setText(f"R$ {res_swing.prejuizo_anterior:,.2f}")
            self.f_st_base.setText(f"R$ {res_swing.base_calculo:,.2f}")
            self.f_st_irrf.setText(f"R$ {res_swing.irpf_retido:,.2f}")
            self.f_st_devido.setText(f"R$ {res_swing.imposto_devido:,.2f}")
            self.f_st_pagar.setText(f"R$ {res_swing.imposto_a_pagar:,.2f}")
            self.f_st_prej_fim.setText(f"R$ {res_swing.prejuizo_acumulado_fim:,.2f}")

        if res_dt:
            self.f_dt_vendas.setText(f"R$ {res_dt.total_vendas:,.2f}")
            self.f_dt_bruto.setText(f"R$ {res_dt.lucro_bruto:,.2f}")
            self.f_dt_despesas.setText(f"R$ {res_dt.despesas:,.2f}")
            self.f_dt_liquido.setText(f"R$ {res_dt.lucro_liquido_mes:,.2f}")
            self.f_dt_prej_ant.setText(f"R$ {res_dt.prejuizo_anterior:,.2f}")
            self.f_dt_base.setText(f"R$ {res_dt.base_calculo:,.2f}")
            self.f_dt_irrf.setText(f"R$ {res_dt.irpf_retido:,.2f}")
            self.f_dt_devido.setText(f"R$ {res_dt.imposto_devido:,.2f}")
            self.f_dt_pagar.setText(f"R$ {res_dt.imposto_a_pagar:,.2f}")
            self.f_dt_prej_fim.setText(f"R$ {res_dt.prejuizo_acumulado_fim:,.2f}")

        # Resumo Anual
        res_anual = self.tax_service.calculate_year_to_date(ano, up_to_month=mes)
        self.f_anual_isento.setText(f"R$ {res_anual.lucro_liquido_isento_menor_20k:,.2f}")
        self.f_anual_tributavel.setText(f"R$ {res_anual.lucro_liquido_tributavel:,.2f}")
        self.f_anual_irrf.setText(f"R$ {res_anual.irpf_retido_total:,.2f}")
        self.f_anual_pago.setText(f"R$ {res_anual.imposto_pago_total:,.2f}")
        self.f_anual_prej.setText(f"R$ {res_anual.prejuizo_acumulado_fim:,.2f}")

