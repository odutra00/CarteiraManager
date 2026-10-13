from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.database import Database
from core.market_data import MarketDataService
from core.models import IndicadoresAtivo


class IndicatorFetchThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, market_data: MarketDataService, ticker: str):
        super().__init__()
        self.market_data = market_data
        self.ticker = ticker

    def run(self):
        indicators = self.market_data.get_indicators(self.ticker)
        self.finished.emit(indicators)


class IndicatorCard(QWidget):
    def __init__(self, title: str, value: str = "-", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        self.setStyleSheet(
            """
            IndicatorCard {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
            }
            """
        )

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: bold;")
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: bold;")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)

    def set_value(self, val: str, color: str = "#ffffff"):
        self.lbl_value.setText(val)
        self.lbl_value.setStyleSheet(f"color: {color}; font-size: 15px; font-weight: bold;")


class IndicatorsTab(QWidget):
    """Aba de Consulta de Indicadores Fundamentalistas e Técnicos de Ações."""

    def __init__(self, db: Database, market_data: MarketDataService, parent=None):
        super().__init__(parent)
        self.db = db
        self.market_data = market_data

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Barra de Pesquisa
        search_group = QGroupBox("Buscar Ativo")
        search_layout = QHBoxLayout(search_group)

        search_layout.addWidget(QLabel("Ticker:"))
        self.cb_ticker = QComboBox()
        self.cb_ticker.setEditable(True)
        self.refresh_tickers()
        search_layout.addWidget(self.cb_ticker)

        self.btn_buscar = QPushButton("Buscar Indicadores")
        self.btn_buscar.setStyleSheet("font-weight: bold; padding: 6px 15px;")
        self.btn_buscar.clicked.connect(self.fetch_indicators)
        search_layout.addWidget(self.btn_buscar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)
        search_layout.addWidget(self.progress_bar)

        search_layout.addStretch()
        main_layout.addWidget(search_group)

        # Painel de Resultados
        results_group = QGroupBox("Painel Fundamentalista")
        results_layout = QGridLayout(results_group)
        results_layout.setSpacing(12)

        self.c_nome = IndicatorCard("Empresa / Nome")
        self.c_cotacao = IndicatorCard("Cotação Atual")
        self.c_variacao = IndicatorCard("Variação do Dia")
        self.c_pl = IndicatorCard("P/L (Preço / Lucro)")
        self.c_dy = IndicatorCard("Dividend Yield (%)")
        self.c_pvp = IndicatorCard("P/VP (Preço / V.P.)")
        self.c_lpa = IndicatorCard("LPA (Lucro por Ação)")
        self.c_beta = IndicatorCard("Beta")
        self.c_52w = IndicatorCard("Faixa 52 Semanas (Mín - Máx)")
        self.c_day_range = IndicatorCard("Faixa do Dia (Mín - Máx)")
        self.c_setor = IndicatorCard("Setor Econômico")

        results_layout.addWidget(self.c_nome, 0, 0, 1, 2)
        results_layout.addWidget(self.c_cotacao, 0, 2)
        results_layout.addWidget(self.c_variacao, 0, 3)

        results_layout.addWidget(self.c_pl, 1, 0)
        results_layout.addWidget(self.c_dy, 1, 1)
        results_layout.addWidget(self.c_pvp, 1, 2)
        results_layout.addWidget(self.c_lpa, 1, 3)

        results_layout.addWidget(self.c_beta, 2, 0)
        results_layout.addWidget(self.c_52w, 2, 1)
        results_layout.addWidget(self.c_day_range, 2, 2)
        results_layout.addWidget(self.c_setor, 2, 3)

        main_layout.addWidget(results_group)
        main_layout.addStretch()

    def refresh_tickers(self):
        current_text = self.cb_ticker.currentText()
        tickers = self.db.get_distinct_tickers()
        self.cb_ticker.clear()
        self.cb_ticker.addItems(tickers)
        if current_text:
            self.cb_ticker.setEditText(current_text)

    def fetch_indicators(self):
        ticker = self.cb_ticker.currentText().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Aviso", "Por favor, digite ou selecione um ticker.")
            return

        self.btn_buscar.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.thread = IndicatorFetchThread(self.market_data, ticker)
        self.thread.finished.connect(self._on_indicators_loaded)
        self.thread.start()

    def _on_indicators_loaded(self, ind: Optional[IndicadoresAtivo]):
        self.btn_buscar.setEnabled(True)
        self.progress_bar.setVisible(False)

        if not ind:
            QMessageBox.warning(
                self, "Não Encontrado",
                "Não foi possível obter dados para o ticker informado. Verifique a conexão com a internet."
            )
            return

        self.c_nome.set_value(ind.nome or ind.ticker)
        self.c_cotacao.set_value(f"R$ {ind.cotacao:,.2f}")

        cor_var = "#4caf50" if ind.variacao_dia_pct >= 0 else "#ef5350"
        self.c_variacao.set_value(f"{ind.variacao_dia_pct:+.2f} %", color=cor_var)

        self.c_pl.set_value(f"{ind.pl:.2f}" if ind.pl is not None else "-")
        self.c_dy.set_value(f"{ind.dy:.2f} %" if ind.dy is not None else "-")
        self.c_pvp.set_value(f"{ind.pvp:.2f}" if ind.pvp is not None else "-")
        self.c_lpa.set_value(f"R$ {ind.lpa:.2f}" if ind.lpa is not None else "-")
        self.c_beta.set_value(f"{ind.beta:.2f}" if ind.beta is not None else "-")

        faixa_52 = "-"
        if ind.minima_52s is not None and ind.maxima_52s is not None:
            faixa_52 = f"R$ {ind.minima_52s:.2f} - R$ {ind.maxima_52s:.2f}"
        self.c_52w.set_value(faixa_52)

        faixa_dia = "-"
        if ind.minima_dia is not None and ind.maxima_dia is not None:
            faixa_dia = f"R$ {ind.minima_dia:.2f} - R$ {ind.maxima_dia:.2f}"
        self.c_day_range.set_value(faixa_dia)

        self.c_setor.set_value(ind.setor or "-")

