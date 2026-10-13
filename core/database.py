import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from core.models import Operacao

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "STOCKS.db"


class Database:
    """Gerenciador do banco de dados SQLite para o CarteiraManager."""

    def __init__(self, db_path: Union[str, Path] = DEFAULT_DB_PATH):
        self.db_path = str(db_path)
        self._is_memory = self.db_path == ":memory:"
        self._memory_conn: Optional[sqlite3.Connection] = None
        if self._is_memory:
            self._memory_conn = sqlite3.connect(":memory:")
            self._memory_conn.row_factory = sqlite3.Row
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        if self._is_memory and self._memory_conn is not None:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Cria a tabela STOCKS caso não exista."""
        with self.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS STOCKS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mercado TEXT,
                    papel TEXT,
                    status TEXT,
                    data DATE,
                    mes INTEGER,
                    ano INTEGER,
                    valor DOUBLE,
                    pm DOUBLE,
                    quantidade INTEGER,
                    qconsolidado INTEGER,
                    custos DOUBLE,
                    consolidado TEXT,
                    valorAtual DOUBLE,
                    dataFechamento DATE,
                    dayTrade INTEGER
                )
                """
            )

    @staticmethod
    def _parse_date(date_val) -> datetime:
        if isinstance(date_val, datetime):
            return date_val
        if isinstance(date_val, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(date_val, fmt)
                except ValueError:
                    continue
        return datetime.now()

    def _row_to_operacao(self, row: sqlite3.Row) -> Operacao:
        raw_data = row["data"]
        dt = self._parse_date(raw_data)

        raw_fechamento = row["dataFechamento"]
        dt_fechamento = self._parse_date(raw_fechamento) if raw_fechamento else None

        valor_atual = None
        if row["valorAtual"] is not None and row["valorAtual"] != "":
            try:
                valor_atual = float(row["valorAtual"])
            except (ValueError, TypeError):
                valor_atual = None

        pm = 0.0
        if row["pm"] is not None and row["pm"] != "":
            try:
                pm = float(row["pm"])
            except (ValueError, TypeError):
                pm = 0.0

        qconsolidado = 0
        if row["qconsolidado"] is not None and row["qconsolidado"] != "":
            try:
                qconsolidado = int(row["qconsolidado"])
            except (ValueError, TypeError):
                qconsolidado = 0

        custos = 0.0
        if row["custos"] is not None and row["custos"] != "":
            try:
                custos = float(row["custos"])
            except (ValueError, TypeError):
                custos = 0.0

        day_trade = 0
        if row["dayTrade"] is not None and row["dayTrade"] != "":
            try:
                day_trade = int(row["dayTrade"])
            except (ValueError, TypeError):
                day_trade = 0

        return Operacao(
            id=row["id"],
            mercado=row["mercado"] or "Vista",
            papel=row["papel"] or "",
            status=row["status"] or "Compra",
            data=dt,
            mes=row["mes"] if row["mes"] is not None else dt.month,
            ano=row["ano"] if row["ano"] is not None else dt.year,
            valor=float(row["valor"]) if row["valor"] is not None else 0.0,
            pm=pm,
            quantidade=int(row["quantidade"]) if row["quantidade"] is not None else 0,
            qconsolidado=qconsolidado,
            custos=custos,
            consolidado=str(row["consolidado"] or "FALSE").upper(),
            valor_atual=valor_atual,
            data_fechamento=dt_fechamento,
            day_trade=day_trade,
        )

    def insert(self, op: Operacao) -> int:
        """Insere uma operação e retorna o ID gerado."""
        data_str = op.data.strftime("%Y-%m-%d %H:%M:%S")
        fechamento_str = (
            op.data_fechamento.strftime("%Y-%m-%d %H:%M:%S")
            if op.data_fechamento
            else ""
        )
        valor_atual_str = str(op.valor_atual) if op.valor_atual is not None else ""

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO STOCKS (
                    mercado, papel, status, data, mes, ano, valor, pm,
                    quantidade, qconsolidado, custos, consolidado, valorAtual,
                    dataFechamento, dayTrade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    op.mercado,
                    op.papel,
                    op.status,
                    data_str,
                    op.data.month,
                    op.data.year,
                    op.valor,
                    op.pm,
                    op.quantidade,
                    op.qconsolidado,
                    op.custos,
                    op.consolidado,
                    valor_atual_str,
                    fechamento_str,
                    op.day_trade,
                ),
            )
            return cursor.lastrowid

    def update(self, op: Operacao):
        """Atualiza todos os campos de uma operação existente."""
        if op.id is None:
            raise ValueError("Operação não possui ID para atualizar.")

        data_str = op.data.strftime("%Y-%m-%d %H:%M:%S")
        fechamento_str = (
            op.data_fechamento.strftime("%Y-%m-%d %H:%M:%S")
            if op.data_fechamento
            else ""
        )
        valor_atual_str = str(op.valor_atual) if op.valor_atual is not None else ""

        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE STOCKS SET
                    mercado=?, papel=?, status=?, data=?, mes=?, ano=?,
                    valor=?, pm=?, quantidade=?, qconsolidado=?, custos=?,
                    consolidado=?, valorAtual=?, dataFechamento=?, dayTrade=?
                WHERE id=?
                """,
                (
                    op.mercado,
                    op.papel,
                    op.status,
                    data_str,
                    op.data.month,
                    op.data.year,
                    op.valor,
                    op.pm,
                    op.quantidade,
                    op.qconsolidado,
                    op.custos,
                    op.consolidado,
                    valor_atual_str,
                    fechamento_str,
                    op.day_trade,
                    op.id,
                ),
            )

    def delete(self, op_id: int):
        """Remove a operação pelo ID."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM STOCKS WHERE id = ?", (op_id,))

    def get_all(self) -> List[Operacao]:
        """Retorna todas as operações ordenadas cronologicamente."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM STOCKS ORDER BY data ASC, id ASC")
            return [self._row_to_operacao(row) for row in cursor.fetchall()]

    def get_by_id(self, op_id: int) -> Optional[Operacao]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM STOCKS WHERE id = ?", (op_id,))
            row = cursor.fetchone()
            return self._row_to_operacao(row) if row else None

    def get_distinct_tickers(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT papel FROM STOCKS ORDER BY papel ASC")
            return [row["papel"] for row in cursor.fetchall() if row["papel"]]

    def get_by_ticker(self, ticker: str) -> List[Operacao]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM STOCKS WHERE papel = ? ORDER BY data ASC, id ASC",
                (ticker.upper(),),
            )
            return [self._row_to_operacao(row) for row in cursor.fetchall()]

    def get_by_month_and_year(self, month: int, year: int) -> List[Operacao]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM STOCKS WHERE mes = ? AND ano = ? ORDER BY data ASC, id ASC",
                (month, year),
            )
            return [self._row_to_operacao(row) for row in cursor.fetchall()]

    def get_consolidated_active(self) -> List[Operacao]:
        """Retorna as operações mais recentes de cada papel com posição em aberto (> 0)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM STOCKS WHERE consolidado = 'TRUE' AND qconsolidado > 0 ORDER BY papel ASC"
            )
            return [self._row_to_operacao(row) for row in cursor.fetchall()]

    def get_earliest_date(self) -> Optional[datetime]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT min(data) as min_data FROM STOCKS")
            row = cursor.fetchone()
            if row and row["min_data"]:
                return self._parse_date(row["min_data"])
        return None

    def search(
        self,
        mercado: str = "",
        papel: str = "",
        status: str = "",
        ano: Optional[int] = None,
        mes: Optional[int] = None,
    ) -> List[Operacao]:
        query = "SELECT * FROM STOCKS WHERE 1=1"
        params = []
        if mercado:
            query += " AND mercado = ?"
            params.append(mercado)
        if papel:
            query += " AND papel = ?"
            params.append(papel.upper())
        if status:
            query += " AND status = ?"
            params.append(status)
        if ano:
            query += " AND ano = ?"
            params.append(ano)
        if mes:
            query += " AND mes = ?"
            params.append(mes)
        query += " ORDER BY data ASC, id ASC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            return [self._row_to_operacao(row) for row in cursor.fetchall()]
