import sys
from pathlib import Path

import qdarkstyle
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.csv_service import CsvService
from core.database import Database
from core.market_data import MarketDataService
from core.portfolio_service import PortfolioService
from core.tax_service import TaxService
from ui.widgets.indicators_tab import IndicatorsTab
from ui.widgets.operations_tab import OperationsTab
from ui.widgets.performance_tab import PerformanceTab
from ui.widgets.portfolio_tab import PortfolioTab
from ui.widgets.tax_tab import TaxTab


class MainWindow(QMainWindow):
    """Janela Principal do CarteiraManager."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CarteiraManager - Gestão de Ativos & IRPF")
        self.resize(1280, 800)

        # Ícone da aplicação
        icon_path = Path(__file__).resolve().parent.parent / "ico2.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Serviços Centrais
        self.db = Database()
        self.portfolio_service = PortfolioService(self.db)
        self.tax_service = TaxService(self.db)
        self.market_data = MarketDataService()
        self.csv_service = CsvService(self.db, self.portfolio_service)

        # Estado visual
        self.dark_mode = True

        self._init_ui()
        self._init_menus()
        self._update_status_bar()

    def _init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # 1. Aba Operações
        self.tab_operations = OperationsTab(self.db, self.portfolio_service)
        self.tab_operations.operations_changed.connect(self._on_operations_changed)

        # 2. Aba Carteira Consolidada
        self.tab_portfolio = PortfolioTab(
            self.db, self.portfolio_service, self.market_data
        )

        # 3. Aba Desempenho
        self.tab_performance = PerformanceTab(
            self.db, self.portfolio_service, self.market_data
        )

        # 4. Aba IRPF
        self.tab_tax = TaxTab(self.db, self.tax_service)

        # 5. Aba Indicadores
        self.tab_indicators = IndicatorsTab(self.db, self.market_data)

        self.tabs.addTab(self.tab_operations, "📋 Operações")
        self.tabs.addTab(self.tab_portfolio, "💼 Carteira Consolidada")
        self.tabs.addTab(self.tab_performance, "📈 Desempenho vs IBOV")
        self.tabs.addTab(self.tab_tax, "🏛️ IRPF & DARF")
        self.tabs.addTab(self.tab_indicators, "🔍 Indicadores")

        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _init_menus(self):
        menubar = self.menuBar()

        # Menu Arquivo
        menu_arquivo = menubar.addMenu("&Arquivo")

        act_import = menu_arquivo.addAction("📥 Importar CSV...")
        act_import.triggered.connect(self._import_csv)

        act_export = menu_arquivo.addAction("📤 Exportar CSV...")
        act_export.triggered.connect(self._export_csv)

        menu_arquivo.addSeparator()
        act_sair = menu_arquivo.addAction("❌ Sair")
        act_sair.triggered.connect(self.close)

        # Menu Ferramentas
        menu_ferramentas = menubar.addMenu("&Ferramentas")
        act_recalcular = menu_ferramentas.addAction("🔄 Recalcular Toda a Carteira")
        act_recalcular.triggered.connect(self._recalculate_all)

        act_quotes = menu_ferramentas.addAction("📊 Atualizar Cotações em Tempo Real")
        act_quotes.triggered.connect(self.tab_portfolio._fetch_quotes_async)

        # Menu Exibir
        menu_exibir = menubar.addMenu("&Exibir")
        self.act_tema = menu_exibir.addAction("🌓 Alternar Modo Claro / Escuro")
        self.act_tema.triggered.connect(self._toggle_theme)

        # Menu Ajuda
        menu_ajuda = menubar.addMenu("&Ajuda")
        act_sobre = menu_ajuda.addAction("ℹ️ Sobre o CarteiraManager")
        act_sobre.triggered.connect(self._show_about)

    def _update_status_bar(self):
        total_ops = len(self.db.get_all())
        distinct_tickers = len(self.db.get_distinct_tickers())
        self.status_bar.showMessage(
            f"Banco de Dados Conectado | {total_ops} operações cadastradas | {distinct_tickers} ativos negociados"
        )

    def _on_operations_changed(self):
        """Disparado quando operações são adicionadas, editadas ou removidas."""
        self.tab_portfolio.refresh()
        self.tab_tax.calculate()
        self.tab_indicators.refresh_tickers()
        self._update_status_bar()

    def _recalculate_all(self):
        self.portfolio_service.recalculate_all()
        self.tab_operations.refresh_table()
        self._on_operations_changed()
        QMessageBox.information(
            self, "Recálculo Concluído", "Todas as posições e preços médios foram recalculados!"
        )

    def _import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Planilha de Operações", "", "Arquivos CSV (*.csv);;Todos os Arquivos (*)"
        )
        if not file_path:
            return

        imported, warnings = self.csv_service.import_csv(file_path)
        self.tab_operations.refresh_table()
        self._on_operations_changed()

        msg = f"Foram importadas {imported} operações com sucesso!"
        if warnings:
            msg += "\n\nAvisos:\n" + "\n".join(warnings[:5])
        QMessageBox.information(self, "Importação Concluída", msg)

    def _export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Planilha de Operações", "CarteiraExport.csv", "Arquivos CSV (*.csv)"
        )
        if not file_path:
            return

        total = self.csv_service.export_csv(file_path)
        QMessageBox.information(
            self, "Exportação Concluída", f"Foram exportadas {total} operações com sucesso!"
        )

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        app = QApplication.instance()
        if self.dark_mode:
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt6"))
        else:
            app.setStyleSheet("")

    def _show_about(self):
        QMessageBox.about(
            self,
            "Sobre o CarteiraManager",
            "<h2>CarteiraManager V2.0</h2>"
            "<p><b>Gerenciador de Carteiras de Ações, B3 e IRPF</b></p>"
            "<p>Arquitetura totalmente refatorada e reativada com <b>PyQt6</b> e <b>yfinance</b>.</p>"
            "<ul>"
            "<li>Cálculo automático de Preço Médio (IN RFB 1.585/2015)</li>"
            "<li>Apuração mensal e anual de IRPF (Swing Trade e Day Trade)</li>"
            "<li>Compensação contínua de prejuízos acumulados</li>"
            "<li>Gráficos interativos de alocação e desempenho vs IBOV</li>"
            "<li>Importação e exportação de planilhas CSV</li>"
            "</ul>"
            "<p>Autor original: Odilon de Oliveira Dutra</p>",
        )


def launch():
    """Inicia a aplicação gráfica."""
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt6"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

