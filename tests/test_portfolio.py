from datetime import datetime
import pytest

from core.database import Database
from core.models import Operacao
from core.portfolio_service import PortfolioService


@pytest.fixture
def memory_db():
    db = Database(":memory:")
    return db


def test_preco_medio_e_consolidacao(memory_db):
    service = PortfolioService(memory_db)

    # 1. Primeira compra: 100 @ 20.00 (custo 10.00)
    # PM com custos: ((100 * 20) + 10) / 100 = 20.10
    op1 = Operacao(
        mercado="Vista",
        papel="PETR4",
        status="Compra",
        data=datetime(2023, 1, 10),
        valor=20.0,
        quantidade=100,
        custos=10.0,
    )
    memory_db.insert(op1)

    # 2. Segunda compra: 100 @ 30.00 (custo 10.00)
    # Custo anterior: 100 * 20.10 = 2010.00
    # Custo novo: (100 * 30) + 10 = 3010.00
    # Total: 5020.00 / 200 = 25.10
    op2 = Operacao(
        mercado="Vista",
        papel="PETR4",
        status="Compra",
        data=datetime(2023, 2, 10),
        valor=30.0,
        quantidade=100,
        custos=10.0,
    )
    memory_db.insert(op2)

    # 3. Venda parcial: 50 @ 35.00
    # PM deve continuar 25.10, quantidade vai para 150
    op3 = Operacao(
        mercado="Vista",
        papel="PETR4",
        status="Venda",
        data=datetime(2023, 3, 10),
        valor=35.0,
        quantidade=50,
        custos=5.0,
    )
    memory_db.insert(op3)

    ops = service.recalculate_all(include_costs_in_pm=True)

    assert len(ops) == 3
    assert ops[0].pm == 20.10
    assert ops[0].qconsolidado == 100
    assert ops[0].consolidado == "FALSE"

    assert ops[1].pm == 25.10
    assert ops[1].qconsolidado == 200
    assert ops[1].consolidado == "FALSE"

    assert ops[2].pm == 25.10
    assert ops[2].qconsolidado == 150
    assert ops[2].consolidado == "TRUE"


def test_posicao_zerada_e_recompra(memory_db):
    service = PortfolioService(memory_db)

    # Compra 100 @ 10
    memory_db.insert(
        Operacao(
            mercado="Vista",
            papel="VALE3",
            status="Compra",
            data=datetime(2023, 1, 1),
            valor=10.0,
            quantidade=100,
            custos=0.0,
        )
    )
    # Vende 100 @ 15 -> zerou
    memory_db.insert(
        Operacao(
            mercado="Vista",
            papel="VALE3",
            status="Venda",
            data=datetime(2023, 1, 15),
            valor=15.0,
            quantidade=100,
            custos=0.0,
        )
    )
    # Recompra 50 @ 20 -> novo PM deve ser 20
    memory_db.insert(
        Operacao(
            mercado="Vista",
            papel="VALE3",
            status="Compra",
            data=datetime(2023, 2, 1),
            valor=20.0,
            quantidade=50,
            custos=0.0,
        )
    )

    ops = service.recalculate_all(include_costs_in_pm=True)
    assert ops[0].qconsolidado == 100
    assert ops[1].qconsolidado == 0
    assert ops[2].qconsolidado == 50
    assert ops[2].pm == 20.0
    assert ops[2].consolidado == "TRUE"


def test_deteccao_day_trade(memory_db):
    service = PortfolioService(memory_db)

    # Compra e venda no mesmo dia -> Day Trade
    dt_same = datetime(2023, 5, 20)
    memory_db.insert(
        Operacao(
            mercado="Vista",
            papel="MGLU3",
            status="Compra",
            data=dt_same,
            valor=3.0,
            quantidade=1000,
            custos=5.0,
        )
    )
    memory_db.insert(
        Operacao(
            mercado="Vista",
            papel="MGLU3",
            status="Venda",
            data=dt_same,
            valor=3.5,
            quantidade=1000,
            custos=5.0,
        )
    )

    # Outro dia qualquer -> Não é Day Trade
    memory_db.insert(
        Operacao(
            mercado="Vista",
            papel="WEGE3",
            status="Compra",
            data=datetime(2023, 5, 21),
            valor=40.0,
            quantidade=100,
            custos=5.0,
        )
    )

    ops = service.recalculate_all()
    mglu_ops = [op for op in ops if op.papel == "MGLU3"]
    wege_ops = [op for op in ops if op.papel == "WEGE3"]

    assert mglu_ops[0].day_trade == 1
    assert mglu_ops[1].day_trade == 1
    assert wege_ops[0].day_trade == 0

