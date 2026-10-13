from datetime import datetime
import pytest

from core.database import Database
from core.models import Operacao
from core.portfolio_service import PortfolioService
from core.tax_service import TaxService


@pytest.fixture
def tax_env():
    db = Database(":memory:")
    portfolio_service = PortfolioService(db)
    tax_service = TaxService(db)
    return db, portfolio_service, tax_service


def test_isencao_vendas_abaixo_20k(tax_env):
    db, portfolio, tax = tax_env

    # Compra 100 @ 50 (5.000)
    db.insert(
        Operacao(
            mercado="Vista",
            papel="VALE3",
            status="Compra",
            data=datetime(2023, 1, 5),
            valor=50.0,
            quantidade=100,
            custos=10.0,
        )
    )
    # Venda 100 @ 60 (6.000) -> Vendas < 20.000 -> Isento
    db.insert(
        Operacao(
            mercado="Vista",
            papel="VALE3",
            status="Venda",
            data=datetime(2023, 1, 20),
            valor=60.0,
            quantidade=100,
            custos=10.0,
        )
    )
    portfolio.recalculate_all()

    res_swing, res_dt, losses = tax.calculate_month(2023, 1)

    assert res_swing.total_vendas == 6000.0
    assert res_swing.isento is True
    assert res_swing.imposto_devido == 0.0
    assert res_swing.imposto_a_pagar == 0.0


def test_tributacao_vendas_acima_20k(tax_env):
    db, portfolio, tax = tax_env

    # Compra 1000 @ 20 (20.000)
    db.insert(
        Operacao(
            mercado="Vista",
            papel="PETR4",
            status="Compra",
            data=datetime(2023, 2, 5),
            valor=20.0,
            quantidade=1000,
            custos=0.0,
        )
    )
    # Venda 1000 @ 30 (30.000) -> Vendas > 20.000 -> Tributável 15%
    # Lucro bruto = 30.000 - 20.000 = 10.000
    # Despesas = 50.00
    # Lucro líquido = 9.950,00
    # Imposto devido = 9.950 * 15% = 1.492,50
    # Dedo duro (0,005% de 30.000) = 1,50
    # Imposto a pagar = 1.492,50 - 1,50 = 1.491,00
    db.insert(
        Operacao(
            mercado="Vista",
            papel="PETR4",
            status="Venda",
            data=datetime(2023, 2, 20),
            valor=30.0,
            quantidade=1000,
            custos=50.0,
        )
    )
    portfolio.recalculate_all(include_costs_in_pm=False)

    res_swing, res_dt, losses = tax.calculate_month(2023, 2)

    assert res_swing.total_vendas == 30000.0
    assert res_swing.isento is False
    assert res_swing.lucro_bruto == 10000.0
    assert res_swing.despesas == 50.0
    assert res_swing.lucro_liquido_mes == 9950.0
    assert res_swing.irpf_retido == 1.50
    assert res_swing.imposto_devido == 1492.50
    assert res_swing.imposto_a_pagar == 1491.00


def test_compensacao_prejuizo_acumulado(tax_env):
    db, portfolio, tax = tax_env

    # Mês 1: Prejuízo de 2.000 em vendas > 20k
    db.insert(
        Operacao(
            mercado="Vista",
            papel="BBDC4",
            status="Compra",
            data=datetime(2023, 3, 1),
            valor=25.0,
            quantidade=1000,
            custos=0.0,
        )
    )
    db.insert(
        Operacao(
            mercado="Vista",
            papel="BBDC4",
            status="Venda",
            data=datetime(2023, 3, 25),
            valor=23.0,
            quantidade=1000,
            custos=0.0,
        )
    )

    # Mês 2: Lucro de 5.000 em vendas > 20k
    # Base de cálculo deve ser 5.000 - 2.000 (prejuízo anterior) = 3.000
    # Imposto devido = 3.000 * 15% = 450.00
    db.insert(
        Operacao(
            mercado="Vista",
            papel="ITUB4",
            status="Compra",
            data=datetime(2023, 4, 1),
            valor=25.0,
            quantidade=1000,
            custos=0.0,
        )
    )
    db.insert(
        Operacao(
            mercado="Vista",
            papel="ITUB4",
            status="Venda",
            data=datetime(2023, 4, 25),
            valor=30.0,
            quantidade=1000,
            custos=0.0,
        )
    )

    portfolio.recalculate_all(include_costs_in_pm=False)

    # Mês 1
    res1, _, losses1 = tax.calculate_month(2023, 3)
    assert res1.lucro_liquido_mes == -2000.0
    assert res1.imposto_a_pagar == 0.0
    assert losses1["swing"] == 2000.0

    # Mês 2 (com prejuízo carregado)
    res2, _, losses2 = tax.calculate_month(2023, 4, carryover_losses=losses1)
    assert res2.lucro_liquido_mes == 5000.0
    assert res2.prejuizo_anterior == 2000.0
    assert res2.base_calculo == 3000.0
    assert res2.imposto_devido == 450.0
    assert losses2["swing"] == 0.0


def test_apuracao_day_trade(tax_env):
    db, portfolio, tax = tax_env

    # Compra e venda no mesmo dia com lucro
    dt = datetime(2023, 5, 10)
    db.insert(
        Operacao(
            mercado="Vista",
            papel="VALE3",
            status="Compra",
            data=dt,
            valor=70.0,
            quantidade=100,
            custos=5.0,
        )
    )
    db.insert(
        Operacao(
            mercado="Vista",
            papel="VALE3",
            status="Venda",
            data=dt,
            valor=75.0,
            quantidade=100,
            custos=5.0,
        )
    )
    portfolio.recalculate_all(include_costs_in_pm=False)

    _, res_dt, _ = tax.calculate_month(2023, 5)

    assert res_dt.total_vendas == 7500.0
    assert res_dt.lucro_bruto == 500.0
    assert res_dt.despesas == 10.0
    assert res_dt.lucro_liquido_mes == 490.0
    # Day trade: alíquota 20%
    assert res_dt.aliquota == 0.20
    assert res_dt.isento is False
    assert res_dt.irpf_retido == 5.0  # 1% de 500
    assert res_dt.imposto_devido == 98.0  # 490 * 0.20
    assert res_dt.imposto_a_pagar == 93.0  # 98 - 5

