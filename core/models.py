from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class TipoOperacao(str, Enum):
    COMPRA = "Compra"
    VENDA = "Venda"


class TipoMercado(str, Enum):
    VISTA = "Vista"
    OPCOES = "Opções"
    FRACIONARIO = "Fracionário"
    FII = "FII"
    ETF = "ETF"
    BDR = "BDR"


@dataclass
class Operacao:
    id: Optional[int] = None
    mercado: str = "Vista"
    papel: str = ""
    status: str = "Compra"  # "Compra" ou "Venda"
    data: datetime = field(default_factory=datetime.now)
    mes: int = 0
    ano: int = 0
    valor: float = 0.0
    pm: float = 0.0
    quantidade: int = 0
    qconsolidado: int = 0
    custos: float = 0.0
    consolidado: str = "FALSE"  # "TRUE" se for o registro mais recente do papel
    valor_atual: Optional[float] = None
    data_fechamento: Optional[datetime] = None
    day_trade: int = 0  # 1 se day trade, 0 caso contrário

    def __post_init__(self):
        if isinstance(self.data, str):
            # Tenta converter strings comuns
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    self.data = datetime.strptime(self.data, fmt)
                    break
                except ValueError:
                    pass
        if isinstance(self.data, (datetime, date)):
            self.mes = self.data.month
            self.ano = self.data.year
        self.papel = self.papel.strip().upper()
        self.mercado = self.mercado.strip()
        self.status = self.status.strip().capitalize()


@dataclass
class PosicaoConsolidada:
    papel: str
    quantidade: int
    pm: float
    custo_total: float
    cotacao_atual: float = 0.0
    valor_atual: float = 0.0
    lucro_prejuizo: float = 0.0
    rentabilidade_pct: float = 0.0
    participacao_pct: float = 0.0


@dataclass
class ResumoIRPF:
    ano: int
    mes: int
    tipo: str  # "Comum" ou "DayTrade"
    total_vendas: float = 0.0
    lucro_bruto: float = 0.0
    despesas: float = 0.0
    lucro_liquido_mes: float = 0.0
    prejuizo_anterior: float = 0.0
    base_calculo: float = 0.0
    aliquota: float = 0.15
    imposto_devido: float = 0.0
    irpf_retido: float = 0.0  # Dedo-duro
    imposto_a_pagar: float = 0.0
    prejuizo_acumulado_fim: float = 0.0
    isento: bool = False
    rentabilidade_pct: float = 0.0


@dataclass
class ResumoAnualIRPF:
    ano: int
    ate_mes: int
    total_vendas: float = 0.0
    irpf_retido_total: float = 0.0
    despesas_total: float = 0.0
    lucro_bruto_total: float = 0.0
    imposto_pago_total: float = 0.0
    lucro_liquido_isento_menor_20k: float = 0.0  # Vendas <= 20k no mês (ações)
    lucro_liquido_tributavel: float = 0.0        # Vendas > 20k ou Day Trade
    prejuizo_acumulado_fim: float = 0.0


@dataclass
class IndicadoresAtivo:
    ticker: str
    nome: Optional[str] = None
    cotacao: float = 0.0
    variacao_dia_pct: float = 0.0
    fechamento_anterior: Optional[float] = None
    abertura: Optional[float] = None
    minima_dia: Optional[float] = None
    maxima_dia: Optional[float] = None
    minima_52s: Optional[float] = None
    maxima_52s: Optional[float] = None
    pl: Optional[float] = None
    dy: Optional[float] = None
    pvp: Optional[float] = None
    beta: Optional[float] = None
    lpa: Optional[float] = None
    setor: Optional[str] = None

