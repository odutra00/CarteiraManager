from typing import Dict, List

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.database import Database
from core.market_data import MarketDataService
from core.models import PosicaoConsolidada
from core.portfolio_service import PortfolioService


class QuoteFetchThread(QThread):
    """Thread em segundo plano para buscar cotações sem travar a interface."""

    finished = pyqtSignal(dict)

    def __init__(self, market_data: MarketDataService, tickers: List[str]):
        super().__init__()
        self.market_data = market_data
        self.tickers = tickers

    def run(self):
        quotes = self.market_data.get_quotes_bulk(self.tickers)
        self.finished.emit(quotes)


class MetricCard(QFrame):
    """Card visual para exibição de métricas financeiras de destaque."""

    def __init__(self, title: str, value: str = "R$ 0,00", subtitle: str = ""):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            """
            MetricCard {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: bold;")

        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")

        self.lbl_subtitle = QLabel(subtitle)
        self.lbl_subtitle.setStyleSheet("color: #888888; font-size: 10px;")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_subtitle)

    def update_values(self, value: str, subtitle: str = "", color: str = "#ffffff"):
        self.lbl_value.setText(value)
        self.lbl_value.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        self.lbl_subtitle.setText(subtitle)


class PortfolioTab(QWidget):
    """Aba de Visão Consolidada da Carteira e Gráfico de Alocação."""

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
        self.quotes_cache: Dict[str, float] = {}

        self._init_ui()
        self.refresh()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. Cards de Resumo no Topo
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        self.card_investido = MetricCard("TOTAL INVESTIDO (CUSTO)")
        self.card_mercado = MetricCard("VALOR DE MERCADO ATUAL")
        self.card_lucro = MetricCard("LUCRO / PREJUÍZO (R$)")
        self.card_rentabilidade = MetricCard("RENTABILIDADE GLOBAL (%)")

        cards_layout.addWidget(self.card_investido)
        cards_layout.addWidget(self.card_mercado)
        cards_layout.addWidget(self.card_lucro)
        cards_layout.addWidget(self.card_rentabilidade)
        main_layout.addLayout(cards_layout)

        # Barra de Ações e Progresso
        actions_layout = QHBoxLayout()
        self.btn_atualizar = QPushButton("Atualizar Cotações de Mercado")
        self.btn_atualizar.setStyleSheet("font-weight: bold; padding: 6px 12px;")
        self.btn_atualizar.clicked.connect(self._fetch_quotes_async)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)

        actions_layout.addWidget(self.btn_atualizar)
        actions_layout.addWidget(self.progress_bar)
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)

        # 2. Divisão: Tabela de Posições à Esquerda, Gráfico de Alocação à Direita
        splitter = QSplitter()

        # Tabela
        table_group = QGroupBox("Ativos em Custódia")
        table_layout = QVBoxLayout(table_group)
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Papel", "Qtd", "PM", "Custo Total", "Cotação",
            "Valor Atual", "L/P (R$)", "Rentab. %", "Alocação %"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        table_layout.addWidget(self.table)
        splitter.addWidget(table_group)

        # Gráfico Donut/Pie
        chart_group = QGroupBox("Alocação da Carteira")
        chart_layout = QVBoxLayout(chart_group)
        self.figure = Figure(figsize=(5, 4), facecolor="#1e1e1e")
        self.canvas = FigureCanvasQTAgg(self.figure)
        chart_layout.addWidget(self.canvas)
        splitter.addWidget(chart_group)

        splitter.setSizes([600, 450])
        main_layout.addWidget(splitter, stretch=1)

    def refresh(self):
        """Atualiza tabela, métricas e gráfico com os dados consolidados."""
        positions = self.portfolio_service.get_consolidated_positions(self.quotes_cache)

        total_investido = sum(p.custo_total for p in positions)
        total_mercado = sum(p.valor_atual for p in positions)
        total_lucro = total_mercado - total_investido
        total_rentabilidade = (
            ((total_mercado / total_investido) - 1.0) * 100.0 if total_investido > 0 else 0.0
        )

        # Atualizar Cards
        self.card_investido.update_values(f"R$ {total_investido:,.2f}")
        self.card_mercado.update_values(f"R$ {total_mercado:,.2f}")

        cor_lucro = "#4caf50" if total_lucro >= 0 else "#ef5350"
        self.card_lucro.update_values(f"R$ {total_lucro:,.2f}", color=cor_lucro)
        self.card_rentabilidade.update_values(f"{total_rentabilidade:+.2f} %", color=cor_lucro)

        # Atualizar Tabela
        self.table.setRowCount(len(positions))
        for row_idx, pos in enumerate(positions):
            item_papel = QTableWidgetItem(pos.papel)
            item_papel.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.table.setItem(row_idx, 0, item_papel)

            self.table.setItem(row_idx, 1, QTableWidgetItem(str(pos.quantidade)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"R$ {pos.pm:,.2f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"R$ {pos.custo_total:,.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"R$ {pos.cotacao_atual:,.2f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"R$ {pos.valor_atual:,.2f}"))

            item_lp = QTableWidgetItem(f"R$ {pos.lucro_prejuizo:+,.2f}")
            item_lp.setForeground(QColor("#4caf50" if pos.lucro_prejuizo >= 0 else "#ef5350"))
            self.table.setItem(row_idx, 6, item_lp)

            item_rent = QTableWidgetItem(f"{pos.rentabilidade_pct:+.2f} %")
            item_rent.setForeground(QColor("#4caf50" if pos.rentabilidade_pct >= 0 else "#ef5350"))
            self.table.setItem(row_idx, 7, item_rent)

            self.table.setItem(row_idx, 8, QTableWidgetItem(f"{pos.participacao_pct:.1f} %"))

        # Atualizar Gráfico
        self._update_chart(positions)

    def _update_chart(self, positions: List[PosicaoConsolidada]):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#1e1e1e")

        valid_positions = [p for p in positions if p.valor_atual > 0]
        if not valid_positions:
            ax.text(
                0.5, 0.5, "Nenhum ativo com posição em aberto",
                ha="center", va="center", color="#888888", fontsize=12
            )
            self.canvas.draw()
            return

        labels = [p.papel for p in valid_positions]
        sizes = [p.valor_atual for p in valid_positions]

        colors = plt.cm.tab20.colors[:len(labels)]
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor="#1e1e1e", linewidth=2),
        )

        for text in texts:
            text.set_color("#ffffff")
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_color("#ffffff")
            autotext.set_fontsize(8)
            autotext.set_weight("bold")

        ax.set_title("Composição da Carteira", color="#ffffff", fontsize=11, fontweight="bold", pad=10)
        self.figure.tight_layout()
        self.canvas.draw()

    def _fetch_quotes_async(self):
        tickers = self.db.get_distinct_tickers()
        if not tickers:
            return

        self.btn_atualizar.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.thread = QuoteFetchThread(self.market_data, tickers)
        self.thread.finished.connect(self._on_quotes_fetched)
        self.thread.start()

    def _on_quotes_fetched(self, quotes: dict):
        self.quotes_cache.update(quotes)
        self.btn_atualizar.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.refresh()

