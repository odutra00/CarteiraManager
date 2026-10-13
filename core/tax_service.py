from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from core.database import Database
from core.models import Operacao, ResumoAnualIRPF, ResumoIRPF


class TaxService:
    """Serviço responsável pela apuração de IRPF sobre Renda Variável:
    - Swing Trade (Operações Comuns, alíquota 15%, isenção de R$ 20k)
    - Day Trade (Alíquota 20%, sem isenção de 20k)
    - Compensação automática de prejuízos acumulados mês a mês
    - Retenção na fonte (dedo-duro de 0,005% e 1%)
    - Resumo consolidado anual para a declaração de ajuste anual do IRPF
    """

    ALIQUOTA_SWING_TRADE = 0.15
    ALIQUOTA_DAY_TRADE = 0.20
    ALIQUOTA_IRRF_SWING = 0.00005  # 0,005%
    ALIQUOTA_IRRF_DAY_TRADE = 0.01  # 1%
    LIMITE_ISENCAO_ACOES = 20000.00
    VALOR_MINIMO_DARF = 10.00

    def __init__(self, db: Database):
        self.db = db

    def calculate_month(
        self, year: int, month: int, carryover_losses: Optional[Dict[str, float]] = None
    ) -> Tuple[ResumoIRPF, ResumoIRPF, Dict[str, float]]:
        """Calcula a apuração fiscal para um mês específico.
        Retorna (Resumo Swing Trade, Resumo Day Trade, novos prejuízos acumulados).
        """
        carryover_losses = carryover_losses or {"swing": 0.0, "day_trade": 0.0}
        ops = self.db.get_by_month_and_year(month, year)

        # Separar por categoria
        ops_swing = [op for op in ops if op.day_trade == 0]
        ops_day_trade = [op for op in ops if op.day_trade == 1]

        resumo_swing, novo_prej_swing = self._calculate_swing_trade(
            year, month, ops_swing, carryover_losses.get("swing", 0.0)
        )
        resumo_dt, novo_prej_dt = self._calculate_day_trade(
            year, month, ops_day_trade, carryover_losses.get("day_trade", 0.0)
        )

        novos_prejuizos = {"swing": novo_prej_swing, "day_trade": novo_prej_dt}
        return resumo_swing, resumo_dt, novos_prejuizos

    def _calculate_swing_trade(
        self, year: int, month: int, operations: List[Operacao], prejuizo_anterior: float
    ) -> Tuple[ResumoIRPF, float]:
        vendas = [op for op in operations if op.status.strip().capitalize() == "Venda"]

        total_vendas = 0.0
        lucro_bruto = 0.0
        despesas = sum(op.custos for op in operations)

        for v in vendas:
            valor_venda_total = v.quantidade * v.valor
            custo_pm = v.quantidade * v.pm
            total_vendas += valor_venda_total
            lucro_bruto += valor_venda_total - custo_pm

        lucro_liquido_mes = lucro_bruto - despesas

        # IRRF (Dedo-duro): 0,005% sobre o valor da venda se > 1,00
        irrf = total_vendas * self.ALIQUOTA_IRRF_SWING
        if irrf < 1.00:
            irrf = 0.00

        # Regra de isenção: Vendas <= R$ 20.000 no mês para ações
        isento = total_vendas <= self.LIMITE_ISENCAO_ACOES and total_vendas > 0

        imposto_devido = 0.0
        imposto_a_pagar = 0.0
        base_calculo = 0.0
        prejuizo_final = prejuizo_anterior

        if isento:
            # Em mês isento com lucro positivo, não se paga imposto nem abate prejuízo acumulado
            # Se teve prejuízo em mês de vendas < 20k, a RFB permite compensar
            if lucro_liquido_mes < 0:
                prejuizo_final += abs(lucro_liquido_mes)
        else:
            if lucro_liquido_mes < 0:
                # Prejuízo no mês acumula
                prejuizo_final += abs(lucro_liquido_mes)
            else:
                # Lucro no mês tributável: abater prejuízos acumulados
                if prejuizo_anterior > 0:
                    if lucro_liquido_mes > prejuizo_anterior:
                        base_calculo = lucro_liquido_mes - prejuizo_anterior
                        prejuizo_final = 0.0
                    else:
                        base_calculo = 0.0
                        prejuizo_final = prejuizo_anterior - lucro_liquido_mes
                else:
                    base_calculo = lucro_liquido_mes

                imposto_devido = base_calculo * self.ALIQUOTA_SWING_TRADE
                imposto_a_pagar = max(0.0, imposto_devido - irrf)

        resumo = ResumoIRPF(
            ano=year,
            mes=month,
            tipo="Comum (Swing Trade)",
            total_vendas=round(total_vendas, 2),
            lucro_bruto=round(lucro_bruto, 2),
            despesas=round(despesas, 2),
            lucro_liquido_mes=round(lucro_liquido_mes, 2),
            prejuizo_anterior=round(prejuizo_anterior, 2),
            base_calculo=round(base_calculo, 2),
            aliquota=self.ALIQUOTA_SWING_TRADE,
            imposto_devido=round(imposto_devido, 2),
            irpf_retido=round(irrf, 2),
            imposto_a_pagar=round(imposto_a_pagar, 2),
            prejuizo_acumulado_fim=round(prejuizo_final, 2),
            isento=isento,
        )
        return resumo, prejuizo_final

    def _calculate_day_trade(
        self, year: int, month: int, operations: List[Operacao], prejuizo_anterior: float
    ) -> Tuple[ResumoIRPF, float]:
        vendas = [op for op in operations if op.status.strip().capitalize() == "Venda"]

        total_vendas = 0.0
        lucro_bruto = 0.0
        despesas = sum(op.custos for op in operations)

        for v in vendas:
            valor_venda_total = v.quantidade * v.valor
            custo_pm = v.quantidade * v.pm
            total_vendas += valor_venda_total
            lucro_bruto += valor_venda_total - custo_pm

        lucro_liquido_mes = lucro_bruto - despesas

        # IRRF Day Trade: 1% sobre os rendimentos líquidos positivos apurados na operação
        irrf = (lucro_bruto * self.ALIQUOTA_IRRF_DAY_TRADE) if lucro_bruto > 0 else 0.0
        if irrf < 1.00:
            irrf = 0.00

        imposto_devido = 0.0
        imposto_a_pagar = 0.0
        base_calculo = 0.0
        prejuizo_final = prejuizo_anterior

        if lucro_liquido_mes < 0:
            prejuizo_final += abs(lucro_liquido_mes)
        elif lucro_liquido_mes > 0:
            if prejuizo_anterior > 0:
                if lucro_liquido_mes > prejuizo_anterior:
                    base_calculo = lucro_liquido_mes - prejuizo_anterior
                    prejuizo_final = 0.0
                else:
                    base_calculo = 0.0
                    prejuizo_final = prejuizo_anterior - lucro_liquido_mes
            else:
                base_calculo = lucro_liquido_mes

            imposto_devido = base_calculo * self.ALIQUOTA_DAY_TRADE
            imposto_a_pagar = max(0.0, imposto_devido - irrf)

        resumo = ResumoIRPF(
            ano=year,
            mes=month,
            tipo="Day Trade",
            total_vendas=round(total_vendas, 2),
            lucro_bruto=round(lucro_bruto, 2),
            despesas=round(despesas, 2),
            lucro_liquido_mes=round(lucro_liquido_mes, 2),
            prejuizo_anterior=round(prejuizo_anterior, 2),
            base_calculo=round(base_calculo, 2),
            aliquota=self.ALIQUOTA_DAY_TRADE,
            imposto_devido=round(imposto_devido, 2),
            irpf_retido=round(irrf, 2),
            imposto_a_pagar=round(imposto_a_pagar, 2),
            prejuizo_acumulado_fim=round(prejuizo_final, 2),
            isento=False,
        )
        return resumo, prejuizo_final

    def calculate_year_to_date(self, year: int, up_to_month: int = 12) -> ResumoAnualIRPF:
        """Processa cronologicamente todos os meses do ano até o mês solicitado,
        acumulando e compensando prejuízos de forma correta.
        """
        losses = {"swing": 0.0, "day_trade": 0.0}

        total_vendas_ano = 0.0
        irrf_total = 0.0
        despesas_total = 0.0
        lucro_bruto_total = 0.0
        imposto_pago_total = 0.0
        lucro_isento_total = 0.0
        lucro_tributavel_total = 0.0

        for m in range(1, up_to_month + 1):
            res_swing, res_dt, losses = self.calculate_month(year, m, losses)

            # Acumular Swing Trade
            total_vendas_ano += res_swing.total_vendas
            irrf_total += res_swing.irpf_retido
            despesas_total += res_swing.despesas
            lucro_bruto_total += res_swing.lucro_bruto
            imposto_pago_total += res_swing.imposto_a_pagar

            if res_swing.isento and res_swing.lucro_liquido_mes > 0:
                lucro_isento_total += res_swing.lucro_liquido_mes
            elif not res_swing.isento and res_swing.lucro_liquido_mes > 0:
                lucro_tributavel_total += res_swing.lucro_liquido_mes

            # Acumular Day Trade
            total_vendas_ano += res_dt.total_vendas
            irrf_total += res_dt.irpf_retido
            despesas_total += res_dt.despesas
            lucro_bruto_total += res_dt.lucro_bruto
            imposto_pago_total += res_dt.imposto_a_pagar
            if res_dt.lucro_liquido_mes > 0:
                lucro_tributavel_total += res_dt.lucro_liquido_mes

        return ResumoAnualIRPF(
            ano=year,
            ate_mes=up_to_month,
            total_vendas=round(total_vendas_ano, 2),
            irpf_retido_total=round(irrf_total, 2),
            despesas_total=round(despesas_total, 2),
            lucro_bruto_total=round(lucro_bruto_total, 2),
            imposto_pago_total=round(imposto_pago_total, 2),
            lucro_liquido_isento_menor_20k=round(lucro_isento_total, 2),
            lucro_liquido_tributavel=round(lucro_tributavel_total, 2),
            prejuizo_acumulado_fim=round(losses["swing"] + losses["day_trade"], 2),
        )

