from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from core.database import Database
from core.models import Operacao, PosicaoConsolidada


class PortfolioService:
    """Serviço responsável por regras de cálculo contábil de carteira:
    - Preço Médio (PM)
    - Posição Consolidada
    - Detecção de Day-Trade
    - Rentabilidade e Desempenho Histórico
    """

    def __init__(self, db: Database):
        self.db = db

    def recalculate_all(self, include_costs_in_pm: bool = True) -> List[Operacao]:
        """Recalcula cronologicamente PM, quantidade consolidada, flag de consolidado
        e flags de day-trade para todas as operações salvas no banco.
        Persiste as alterações e retorna as operações atualizadas.
        """
        operations = self.db.get_all()
        if not operations:
            return []

        # 1. Agrupar por papel para calcular PM e quantidade consolidada cronologicamente
        ops_by_ticker = defaultdict(list)
        for op in operations:
            ops_by_ticker[op.papel].append(op)

        updated_ops = []

        for ticker, ops in ops_by_ticker.items():
            # Ordenar por data e id
            ops.sort(key=lambda x: (x.data, x.id or 0))

            q_atual = 0
            pm_atual = 0.0

            for i, op in enumerate(ops):
                status = op.status.strip().capitalize()
                qtd = op.quantidade
                preco = op.valor
                custo = op.custos if include_costs_in_pm else 0.0

                if status == "Compra":
                    if q_atual <= 0:
                        # Nova posição
                        novo_pm = ((qtd * preco) + custo) / qtd if qtd > 0 else preco
                        q_atual = qtd
                    else:
                        # Posição existente: média ponderada
                        custo_anterior = q_atual * pm_atual
                        custo_compra = (qtd * preco) + custo
                        novo_pm = (custo_anterior + custo_compra) / (q_atual + qtd)
                        q_atual += qtd
                    pm_atual = round(novo_pm, 4)

                elif status == "Venda":
                    # Na venda, o PM não se altera pelas regras da Receita Federal
                    q_atual = max(0, q_atual - qtd)
                    if q_atual == 0:
                        # Posição foi totalmente encerrada
                        # Mantemos o PM para fins de histórico e cálculo de ganho de capital
                        pass

                op.pm = round(pm_atual, 2)
                op.qconsolidado = q_atual
                # Consolidado True apenas na última operação do papel
                op.consolidado = "TRUE" if i == len(ops) - 1 else "FALSE"
                updated_ops.append(op)

        # 2. Detectar Day-Trade (Compra e Venda do mesmo papel no mesmo dia)
        self._detect_day_trades(updated_ops)

        # 3. Persistir todas as atualizações no banco
        for op in updated_ops:
            self.db.update(op)

        # Reordenar cronologicamente para retorno
        updated_ops.sort(key=lambda x: (x.data, x.id or 0))
        return updated_ops

    @staticmethod
    def _detect_day_trades(operations: List[Operacao]):
        """Marca day_trade = 1 para operações com compra e venda do mesmo ativo no mesmo dia."""
        ops_by_day_ticker = defaultdict(lambda: {"compras": [], "vendas": []})

        for op in operations:
            key = (op.data.strftime("%Y-%m-%d"), op.papel)
            status = op.status.strip().capitalize()
            if status == "Compra":
                ops_by_day_ticker[key]["compras"].append(op)
            elif status == "Venda":
                ops_by_day_ticker[key]["vendas"].append(op)

        for key, groups in ops_by_day_ticker.items():
            is_dt = bool(groups["compras"] and groups["vendas"])
            for op in groups["compras"]:
                op.day_trade = 1 if is_dt else 0
            for op in groups["vendas"]:
                op.day_trade = 1 if is_dt else 0

    def get_consolidated_positions(
        self, quotes_map: Optional[Dict[str, float]] = None
    ) -> List[PosicaoConsolidada]:
        """Retorna lista de posições atualmente abertas (qconsolidado > 0 na última operação)."""
        active_ops = self.db.get_consolidated_active()
        positions: List[PosicaoConsolidada] = []
        quotes_map = quotes_map or {}

        total_portfolio_value = 0.0

        for op in active_ops:
            qtd = op.qconsolidado
            pm = op.pm
            custo_total = qtd * pm
            cotacao = quotes_map.get(op.papel, op.valor_atual or pm)
            if cotacao is None or cotacao <= 0:
                cotacao = pm

            valor_atual = qtd * cotacao
            lucro_prejuizo = valor_atual - custo_total
            rentabilidade = (
                ((valor_atual / custo_total) - 1.0) * 100.0 if custo_total > 0 else 0.0
            )

            total_portfolio_value += valor_atual

            pos = PosicaoConsolidada(
                papel=op.papel,
                quantidade=qtd,
                pm=round(pm, 2),
                custo_total=round(custo_total, 2),
                cotacao_atual=round(cotacao, 2),
                valor_atual=round(valor_atual, 2),
                lucro_prejuizo=round(lucro_prejuizo, 2),
                rentabilidade_pct=round(rentabilidade, 2),
                participacao_pct=0.0,
            )
            positions.append(pos)

        # Atualizar percentual de participação
        if total_portfolio_value > 0:
            for pos in positions:
                pos.participacao_pct = round(
                    (pos.valor_atual / total_portfolio_value) * 100.0, 2
                )

        # Ordenar por valor_atual decrescente
        positions.sort(key=lambda x: x.valor_atual, reverse=True)
        return positions

    def calculate_normalized_performance(
        self, historical_data_map: Dict[str, pd.Series], ibov_series: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """Calcula o histórico de desempenho normalizado da carteira comparado com os ativos e o IBOV.
        Totalmente compatível com Pandas 2.0+ (sem append).
        """
        operations = self.db.get_all()
        if not operations or not historical_data_map:
            return pd.DataFrame()

        # Identificar data de início e término comum
        tickers = list(historical_data_map.keys())
        all_series = [s.dropna() for s in historical_data_map.values() if not s.empty]
        if not all_series:
            return pd.DataFrame()

        # Alinhar todas as séries em um DataFrame
        df_prices = pd.concat([historical_data_map[t].rename(t) for t in tickers if not historical_data_map[t].empty], axis=1)
        df_prices = df_prices.ffill().dropna(how="all")
        if df_prices.empty:
            return pd.DataFrame()

        # Construir série da carteira dia a dia
        result_df = pd.DataFrame(index=df_prices.index)

        # Para cada ativo, normalizar pelo primeiro preço disponível
        for ticker in df_prices.columns:
            first_valid = df_prices[ticker].dropna().iloc[0] if not df_prices[ticker].dropna().empty else None
            if first_valid and first_valid > 0:
                result_df[ticker] = df_prices[ticker] / first_valid

        # Se IBOV fornecido, normalizar pelo primeiro valor
        if ibov_series is not None and not ibov_series.empty:
            ibov_aligned = ibov_series.reindex(df_prices.index).ffill().bfill()
            first_ibov = ibov_aligned.dropna().iloc[0] if not ibov_aligned.dropna().empty else None
            if first_ibov and first_ibov > 0:
                result_df["IBOV"] = ibov_aligned / first_ibov

        # Carteira consolidada ponderada
        # Média simples dos ativos normalizados disponíveis caso não haja posições diárias computadas
        active_cols = [c for c in result_df.columns if c != "IBOV"]
        if active_cols:
            result_df["Carteira"] = result_df[active_cols].mean(axis=1)

        return result_df

