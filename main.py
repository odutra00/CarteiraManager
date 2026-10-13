#!/usr/bin/env python3
"""CarteiraManager - Gerenciador de Carteiras de Ações e Apuração de IRPF.

Ponto de entrada principal da aplicação.
"""

import argparse
import sys
from pathlib import Path

# Garantir que o diretório raiz esteja no path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.database import Database
from core.portfolio_service import PortfolioService
from core.csv_service import CsvService


def run_cli_commands(args) -> bool:
    """Executa comandos CLI opcionais antes de iniciar a interface gráfica."""
    db = Database()
    portfolio = PortfolioService(db)
    csv_service = CsvService(db, portfolio)

    if args.recalculate:
        print("Recalculando toda a carteira e preços médios...")
        portfolio.recalculate_all()
        print("Recálculo concluído com sucesso!")
        return True

    if args.import_csv:
        print(f"Importando operações do arquivo: {args.import_csv}...")
        total, warnings = csv_service.import_csv(args.import_csv)
        print(f"{total} operações importadas com sucesso!")
        if warnings:
            for w in warnings:
                print(f"Aviso: {w}")
        return True

    if args.export_csv:
        print(f"Exportando operações para: {args.export_csv}...")
        total = csv_service.export_csv(args.export_csv)
        print(f"{total} operações exportadas com sucesso!")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="CarteiraManager - Gestão de Ativos & IRPF")
    parser.add_argument("--recalculate", action="store_true", help="Recalcula toda a carteira via terminal")
    parser.add_argument("--import-csv", type=str, help="Importa operações de um arquivo CSV")
    parser.add_argument("--export-csv", type=str, help="Exporta operações para um arquivo CSV")
    parser.add_argument("--version", action="version", version="CarteiraManager 2.0")

    args, remaining = parser.parse_known_args()

    if run_cli_commands(args):
        sys.exit(0)

    # Iniciar interface gráfica PyQt6
    from ui.app import launch
    launch()


if __name__ == "__main__":
    main()
