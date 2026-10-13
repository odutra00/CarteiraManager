from pathlib import Path
import pytest

from core.database import Database
from core.portfolio_service import PortfolioService
from core.csv_service import CsvService


@pytest.fixture
def csv_env(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    portfolio = PortfolioService(db)
    csv_service = CsvService(db, portfolio)
    return db, portfolio, csv_service, tmp_path


def test_import_planilha_teste(csv_env):
    db, portfolio, csv_service, tmp_path = csv_env
    test_csv_path = Path(__file__).resolve().parent.parent / "PlanilhaOperacoesTeste.csv"

    imported, warnings = csv_service.import_csv(test_csv_path)

    assert imported == 8
    assert len(warnings) == 0

    ops = db.get_all()
    assert len(ops) == 8

    # Verificar se recalculo aconteceu
    vale_ops = [op for op in ops if op.papel == "VALE3"]
    assert len(vale_ops) == 5
    # Última operação de VALE3 deve ter consolidado TRUE e quantidade 0 (pois vendeu 100+4+39+43=186)
    last_vale = vale_ops[-1]
    assert last_vale.consolidado == "TRUE"
    assert last_vale.qconsolidado == 0


def test_export_and_reimport(csv_env):
    db, portfolio, csv_service, tmp_path = csv_env
    test_csv_path = Path(__file__).resolve().parent.parent / "PlanilhaOperacoesTeste.csv"

    csv_service.import_csv(test_csv_path)

    export_path = tmp_path / "exported.csv"
    exported_count = csv_service.export_csv(export_path)
    assert exported_count == 8
    assert export_path.exists()

    # Novo banco para reimportar o exportado
    new_db = Database(tmp_path / "reimported.db")
    new_portfolio = PortfolioService(new_db)
    new_csv = CsvService(new_db, new_portfolio)

    reimported_count, _ = new_csv.import_csv(export_path)
    assert reimported_count == 8

