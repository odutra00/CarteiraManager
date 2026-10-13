from datetime import datetime, timedelta
from typing import Dict, List, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import pandas as pd
from PyQt6.QtCore import QDate, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.database import Database
from core.market_data import MarketDataService
from core.portfolio_service import PortfolioService


class PerformanceHistoryThread(QThread):
    """Thread em segundo plano para buscar dados históricos sem travar a interface."""

    finished = pyqtSignal(dict, object)

    def __init__(
        self,
        market_data: MarketDataService,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime,
        include_ibov: bool,
    ):
        super().__init__()
        self.market_data = market_data
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.include_ibov = include_ibov

    def run(self):
        hist_map: Dict[str, pd.Series] = {}
        for ticker in self.tickers:
            s = self.market_data.get_historical_data(ticker, self.start_date, self.end_date)
            if not s.empty:
                hist_map[ticker] = s

        ibov_series = None
        if self.include_ibov:
            ibov_series = self.market_data.get_ibov_history(self.start_date, self.end_date)

        self.finished.emit(hist_map, ibov_series)


class PerformanceTab(QWidget):
    """Aba de Análise e Gráfico de Desempenho Histórico Normalizado."""

    def __init__(
        self,
        db: Database,
        portfolio_service: PortfolioService,
        market_data: MarketDataService,
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.portfolio_service = portfolio_service
        self.market_data = market_data

        self.cached_hist_map: Dict[str, pd.Series] = {}
        self.cached_ibov: Optional[pd.Series] = None

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Barra de Controles
        controls_group = QGroupBox("Controles do Gráfico")
        controls_layout = QHBoxLayout(controls_group)

        earliest = self.db.get_earliest_date() or (datetime.now() - timedelta(days=365))
        controls_layout.addWidget(QLabel("Data Inicial:"))
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate(earliest.year, earliest.month, earliest.day))
        self.date_inicio.setDisplayFormat("dd/MM/yyyy")
        controls_layout.addWidget(self.date_inicio)

        controls_layout.addWidget(QLabel("Data Final:"))
        self.date_fim = QDateEdit()
        self.date_fim.setCalendarPopup(True)
        self.date_fim.setDate(QDate.currentDate())
        self.date_fim.setDisplayFormat("dd/MM/yyyy")
        controls_layout.addWidget(self.date_fim)

        self.chk_carteira = QCheckBox("Carteira")
        self.chk_carteira.setChecked(True)
        self.chk_carteira.stateChanged.connect(self._replot)
        controls_layout.addWidget(self.chk_carteira)

        self.chk_ibov = QCheckBox("Ibovespa (IBOV)")
        self.chk_ibov.setChecked(True)
        self.chk_ibov.stateChanged.connect(self._replot)
        controls_layout.addWidget(self.chk_ibov)

        self.chk_papeis = QCheckBox("Papéis Individuais")
        self.chk_papeis.setChecked(False)
        self.chk_papeis.stateChanged.connect(self._replot)
        controls_layout.addWidget(self.chk_papeis)

        self.btn_atualizar = QPushButton("Atualizar Dados")
        self.btn_atualizar.setStyleSheet("font-weight: bold; padding: 6px 12px;")
        self.btn_atualizar.clicked.connect(self.load_data)
        controls_layout.addWidget(self.btn_atualizar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)
        controls_layout.addWidget(self.progress_bar)

        controls_layout.addStretch()
        main_layout.addWidget(controls_group)

        # Gráfico Matplotlib
        chart_group = QGroupBox("Evolução Comparativa Normalizada (Base 1.0)")
        chart_layout = QVBoxLayout(chart_group)

        self.figure = Figure(figsize=(8, 5), facecolor="#1e1e1e")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        chart_layout.addWidget(self.toolbar)
        chart_layout.addWidget(self.canvas)
        main_layout.addWidget(chart_group, stretch=1)

    def load_data(self):
        """Dispara a busca assíncrona de séries históricas."""
        tickers = self.db.get_distinct_tickers()
        if not tickers:
            return

        dt_inicio = self.date_inicio.date()
        dt_fim = self.date_fim.date()
        start = datetime(dt_inicio.year(), dt_inicio.month(), dt_inicio.day())
        end = datetime(dt_fim.year(), dt_fim.month(), dt_fim.day())

        self.btn_atualizar.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.thread = PerformanceHistoryThread(
            self.market_data, tickers, start, end, self.chk_ibov.isChecked()
        )
        self.thread.finished.connect(self._on_data_loaded)
        self.thread.start()

    def _on_data_loaded(self, hist_map: dict, ibov_series: object):
        self.cached_hist_map = hist_map
        self.cached_ibov = ibov_series
        self.btn_atualizar.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._replot()

    def _replot(self):
        """Redesenha as curvas selecionadas."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#1e1e1e")
        ax.grid(True, linestyle="--", alpha=0.3, color="#555555")

        if not self.cached_hist_map:
            ax.text(
                0.5, 0.5, "Clique em 'Atualizar Dados' para carregar as séries históricas",
                ha="center", va="center", color="#888888", fontsize=12
            )
            self.canvas.draw()
            return

        df_norm = self.portfolio_service.calculate_normalized_performance(
            self.cached_hist_map, self.cached_ibov
        )
        if df_norm.empty:
            ax.text(
                0.5, 0.5, "Sem dados suficientes para o período selecionado",
                ha="center", va="center", color="#888888", fontsize=12
            )
            self.canvas.draw()
            return

        # Filtrar colunas de acordo com as checkboxes
        cols_to_plot = []
        if self.chk_carteira.isChecked() and "Carteira" in df_norm.columns:
            cols_to_plot.append("Carteira")
        if self.chk_ibov.isChecked() and "IBOV" in df_norm.columns:
            cols_to_plot.append("IBOV")
        if self.chk_papeis.isChecked():
            for c in df_norm.columns:
                if c not in ("Carteira", "IBOV"):
                    cols_to_plot.append(c)

        for col in cols_to_plot:
            series = df_norm[col].dropna()
            if series.empty:
                continue

            linewidth = 2.5 if col in ("Carteira", "IBOV") else 1.2
            linestyle = "-" if col != "IBOV" else "--"
            ax.plot(
                series.index, series.values,
                label=col, linewidth=linewidth, linestyle=linestyle
            )

        ax.axhline(1.0, color="#ffffff", linestyle=":", alpha=0.5, label="Base (1.0)")
        ax.set_title("Desempenho Relativo Normalizado", color="#ffffff", fontsize=12, fontweight="bold")
        ax.set_ylabel("Múltiplo de Retorno (1.0 = Inicial)", color="#ffffff")
        ax.tick_params(colors="#ffffff", which="both")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))

        for spine in ax.spines.values():
            spine.set_color("#444444")

        leg = ax.legend(loc="upper left", facecolor="#2b2b2b", edgecolor="#444444")
        for text in leg.get_texts():
            text.set_color("#ffffff")

        self.figure.tight_layout()
        self.canvas.draw()

