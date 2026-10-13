from datetime import datetime
from typing import Callable, Optional

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.database import Database
from core.models import Operacao
from core.portfolio_service import PortfolioService


class OperationsTab(QWidget):
    """Aba de Gerenciamento e Cadastro de Operações."""

    operations_changed = pyqtSignal()

    def __init__(self, db: Database, portfolio_service: PortfolioService, parent=None):
        super().__init__(parent)
        self.db = db
        self.portfolio_service = portfolio_service
        self.selected_op_id: Optional[int] = None

        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 1. Painel Esquerdo: Formulário de Entrada
        form_group = QGroupBox("Cadastro de Operação")
        form_group.setFixedWidth(320)
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        self.cb_mercado = QComboBox()
        self.cb_mercado.addItems(["Vista", "Opções", "Fracionário", "FII", "ETF", "BDR"])

        self.txt_papel = QLineEdit()
        self.txt_papel.setPlaceholderText("Ex: PETR4, VALE3")

        self.cb_status = QComboBox()
        self.cb_status.addItems(["Compra", "Venda"])

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setDisplayFormat("dd/MM/yyyy")

        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0.01, 1_000_000.0)
        self.spin_valor.setDecimals(2)
        self.spin_valor.setPrefix("R$ ")
        self.spin_valor.setValue(10.0)

        self.spin_qtd = QSpinBox()
        self.spin_qtd.setRange(1, 10_000_000)
        self.spin_qtd.setValue(100)

        self.spin_custos = QDoubleSpinBox()
        self.spin_custos.setRange(0.0, 100_000.0)
        self.spin_custos.setDecimals(2)
        self.spin_custos.setPrefix("R$ ")
        self.spin_custos.setValue(0.0)

        form_layout.addRow(QLabel("Mercado:"), self.cb_mercado)
        form_layout.addRow(QLabel("Papel / Ticker:"), self.txt_papel)
        form_layout.addRow(QLabel("Tipo:"), self.cb_status)
        form_layout.addRow(QLabel("Data:"), self.date_picker)
        form_layout.addRow(QLabel("Preço Unitário:"), self.spin_valor)
        form_layout.addRow(QLabel("Quantidade:"), self.spin_qtd)
        form_layout.addRow(QLabel("Custos / Taxas:"), self.spin_custos)

        # Botões de Ação
        btn_layout = QVBoxLayout()
        self.btn_salvar = QPushButton("Salvar Operação")
        self.btn_salvar.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;")
        self.btn_salvar.clicked.connect(self._on_save_operation)

        self.btn_limpar = QPushButton("Limpar / Nova")
        self.btn_limpar.clicked.connect(self._clear_form)

        self.btn_excluir = QPushButton("Excluir Selecionada")
        self.btn_excluir.setStyleSheet("background-color: #c62828; color: white; font-weight: bold; padding: 6px;")
        self.btn_excluir.clicked.connect(self._on_delete_operation)
        self.btn_excluir.setEnabled(False)

        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_limpar)
        btn_layout.addWidget(self.btn_excluir)
        form_layout.addRow(btn_layout)

        main_layout.addWidget(form_group)

        # 2. Painel Direito: Tabela e Filtros
        table_group = QGroupBox("Histórico de Operações")
        table_layout = QVBoxLayout(table_group)

        # Barra de Busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Filtrar por Papel:"))
        self.txt_busca = QLineEdit()
        self.txt_busca.setPlaceholderText("Digite o ticker (ex: VALE3)...")
        self.txt_busca.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.txt_busca)

        self.btn_recalcular = QPushButton("Recalcular Carteira")
        self.btn_recalcular.clicked.connect(self._recalculate)
        search_layout.addWidget(self.btn_recalcular)

        table_layout.addLayout(search_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Mercado", "Papel", "Tipo", "Data", "Preço",
            "PM", "Qtd", "Qtd Cons.", "Custos", "Day-Trade"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_table_row_selected)
        self.table.setAlternatingRowColors(True)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_group, stretch=1)

    def refresh_table(self):
        """Recarrega os registros da tabela a partir do banco de dados."""
        filtro = self.txt_busca.text().strip().upper()
        if filtro:
            ops = self.db.search(papel=filtro)
        else:
            ops = self.db.get_all()

        self.table.setRowCount(len(ops))
        for row_idx, op in enumerate(ops):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(op.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(op.mercado))

            item_papel = QTableWidgetItem(op.papel)
            item_papel.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.table.setItem(row_idx, 2, item_papel)

            item_tipo = QTableWidgetItem(op.status)
            if op.status == "Compra":
                item_tipo.setForeground(QColor("#4caf50"))
            else:
                item_tipo.setForeground(QColor("#ef5350"))
            self.table.setItem(row_idx, 3, item_tipo)

            self.table.setItem(row_idx, 4, QTableWidgetItem(op.data.strftime("%d/%m/%Y")))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"R$ {op.valor:,.2f}"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(f"R$ {op.pm:,.2f}"))
            self.table.setItem(row_idx, 7, QTableWidgetItem(str(op.quantidade)))
            self.table.setItem(row_idx, 8, QTableWidgetItem(str(op.qconsolidado)))
            self.table.setItem(row_idx, 9, QTableWidgetItem(f"R$ {op.custos:,.2f}"))

            dt_text = "SIM" if op.day_trade == 1 else "NÃO"
            item_dt = QTableWidgetItem(dt_text)
            if op.day_trade == 1:
                item_dt.setForeground(QColor("#ff9800"))
            self.table.setItem(row_idx, 10, item_dt)

    def _on_table_row_selected(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.selected_op_id = None
            self.btn_excluir.setEnabled(False)
            return

        row = selected_items[0].row()
        try:
            op_id = int(self.table.item(row, 0).text())
            op = self.db.get_by_id(op_id)
            if op:
                self.selected_op_id = op.id
                self.cb_mercado.setCurrentText(op.mercado)
                self.txt_papel.setText(op.papel)
                self.cb_status.setCurrentText(op.status)
                self.date_picker.setDate(QDate(op.data.year, op.data.month, op.data.day))
                self.spin_valor.setValue(op.valor)
                self.spin_qtd.setValue(op.quantidade)
                self.spin_custos.setValue(op.custos)
                self.btn_salvar.setText("Atualizar Operação")
                self.btn_excluir.setEnabled(True)
        except Exception:
            pass

    def _clear_form(self):
        self.selected_op_id = None
        self.txt_papel.clear()
        self.cb_mercado.setCurrentIndex(0)
        self.cb_status.setCurrentIndex(0)
        self.date_picker.setDate(QDate.currentDate())
        self.spin_valor.setValue(10.0)
        self.spin_qtd.setValue(100)
        self.spin_custos.setValue(0.0)
        self.btn_salvar.setText("Salvar Operação")
        self.btn_excluir.setEnabled(False)
        self.table.clearSelection()

    def _on_save_operation(self):
        papel = self.txt_papel.text().strip().upper()
        if not papel:
            QMessageBox.warning(self, "Aviso", "Por favor, informe o ticker do papel.")
            return

        dt = self.date_picker.date()
        op_data = datetime(dt.year(), dt.month(), dt.day())

        op = Operacao(
            id=self.selected_op_id,
            mercado=self.cb_mercado.currentText(),
            papel=papel,
            status=self.cb_status.currentText(),
            data=op_data,
            valor=self.spin_valor.value(),
            quantidade=self.spin_qtd.value(),
            custos=self.spin_custos.value(),
        )

        if self.selected_op_id:
            self.db.update(op)
        else:
            self.db.insert(op)

        self.portfolio_service.recalculate_all()
        self._clear_form()
        self.refresh_table()
        self.operations_changed.emit()

    def _on_delete_operation(self):
        if not self.selected_op_id:
            return

        res = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir a operação selecionada?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            self.db.delete(self.selected_op_id)
            self.portfolio_service.recalculate_all()
            self._clear_form()
            self.refresh_table()
            self.operations_changed.emit()

    def _on_search_text_changed(self):
        self.refresh_table()

    def _recalculate(self):
        self.portfolio_service.recalculate_all()
        self.refresh_table()
        self.operations_changed.emit()
        QMessageBox.information(self, "Sucesso", "Carteira recalculada com sucesso!")

