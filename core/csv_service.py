import csv
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Union

from core.database import Database
from core.models import Operacao
from core.portfolio_service import PortfolioService


class CsvService:
    """Serviço para importação e exportação de planilhas CSV de operações."""

    def __init__(self, db: Database, portfolio_service: PortfolioService):
        self.db = db
        self.portfolio_service = portfolio_service

    @staticmethod
    def _parse_number(val: str, default: float = 0.0) -> float:
        if not val:
            return default
        clean = str(val).replace("R$", "").replace("$", "").replace(" ", "").strip()
        # Se contiver vírgula, tratar como separador decimal
        clean = clean.replace(",", ".")
        try:
            return float(clean)
        except ValueError:
            return default

    @staticmethod
    def _parse_int(val: str, default: int = 0) -> int:
        if not val:
            return default
        try:
            return int(float(str(val).replace(",", ".").strip()))
        except ValueError:
            return default

    @staticmethod
    def _parse_date(val: str) -> datetime:
        clean = str(val).strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(clean, fmt)
            except ValueError:
                continue
        return datetime.now()

    def import_csv(self, file_path: Union[str, Path]) -> Tuple[int, List[str]]:
        """Importa operações a partir de um arquivo CSV.
        Retorna (número de operações importadas, lista de avisos/erros).
        """
        path = Path(file_path)
        if not path.exists():
            return 0, [f"Arquivo não encontrado: {path}"]

        imported_count = 0
        warnings = []

        # Tentar abrir em diferentes codificações
        content = None
        for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                with open(path, "r", encoding=encoding) as f:
                    content = f.read()
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            return 0, ["Falha ao ler o arquivo: codificação incompatível."]

        # Detectar delimitador (geralmente ; ou ,)
        delimiter = ";" if ";" in content.splitlines()[0] else ","

        lines = content.splitlines()
        reader = csv.DictReader(lines, delimiter=delimiter)

        fieldnames = [f.strip() for f in (reader.fieldnames or [])]
        # Mapeamento case-insensitive de colunas
        field_map = {f.lower(): f for f in fieldnames}

        for row_idx, row in enumerate(reader, start=2):
            try:
                # Normalizar chaves para minúsculas
                row_lower = {k.strip().lower(): v.strip() for k, v in row.items() if k}

                mercado = row_lower.get("mercado", "Vista")
                papel = row_lower.get("papel", "").upper()
                status = row_lower.get("status", "Compra").capitalize()
                raw_data = row_lower.get("data", "")
                raw_valor = row_lower.get("valor", row_lower.get("preço", "0"))
                raw_qtd = row_lower.get("quantidade", row_lower.get("qtd", "0"))
                raw_custos = row_lower.get("custos", "0")

                if not papel:
                    continue

                dt = self._parse_date(raw_data)
                valor = self._parse_number(raw_valor)
                quantidade = self._parse_int(raw_qtd)
                custos = self._parse_number(raw_custos)

                op = Operacao(
                    mercado=mercado,
                    papel=papel,
                    status=status,
                    data=dt,
                    valor=valor,
                    quantidade=quantidade,
                    custos=custos,
                )
                self.db.insert(op)
                imported_count += 1

            except Exception as e:
                warnings.append(f"Linha {row_idx}: Erro ao processar registro ({e})")

        # Recalcular toda a carteira após a importação
        if imported_count > 0:
            self.portfolio_service.recalculate_all()

        return imported_count, warnings

    def export_csv(self, file_path: Union[str, Path]) -> int:
        """Exporta todas as operações do banco de dados para um arquivo CSV formatado."""
        operations = self.db.get_all()
        path = Path(file_path)

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            # Cabeçalho compatível com o sistema original
            writer.writerow([
                "Numero da Operação",
                "Mercado",
                "Papel",
                "Status",
                "Data",
                "Mes",
                "Ano",
                "Valor",
                "PM",
                "Quantidade",
                "Quantidade Consolidada",
                "Custos",
                "Consolidado",
                "Valor Atual",
                "Data de Fechamento",
                "Day-Trade",
            ])

            for op in operations:
                writer.writerow([
                    op.id,
                    op.mercado,
                    op.papel,
                    op.status,
                    op.data.strftime("%d/%m/%Y"),
                    op.mes,
                    op.ano,
                    f"{op.valor:.2f}".replace(".", ","),
                    f"{op.pm:.2f}".replace(".", ","),
                    op.quantidade,
                    op.qconsolidado,
                    f"{op.custos:.2f}".replace(".", ","),
                    op.consolidado,
                    f"{op.valor_atual:.2f}".replace(".", ",") if op.valor_atual else "",
                    op.data_fechamento.strftime("%d/%m/%Y") if op.data_fechamento else "",
                    op.day_trade,
                ])

        return len(operations)

