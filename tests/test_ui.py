import os
import pytest

# Configurar Qt para rodar offscreen nos testes
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication

from ui.app import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_tabs(qapp):
    window = MainWindow()
    assert window.tabs.count() == 5
    assert window.tabs.tabText(0) == "📋 Operações"
    assert window.tabs.tabText(1) == "💼 Carteira Consolidada"
    assert window.tabs.tabText(2) == "📈 Desempenho vs IBOV"
    assert window.tabs.tabText(3) == "🏛️ IRPF & DARF"
    assert window.tabs.tabText(4) == "🔍 Indicadores"

    # Verificar se as operações foram carregadas na tabela
    assert window.tab_operations.table.rowCount() >= 40
    # Verificar se a aba de carteira consolidada calculou
    assert window.tab_portfolio.table.rowCount() > 0

