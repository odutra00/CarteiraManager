import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

try:
    import yfinance as yf
except ImportError:
    yf = None

from core.models import IndicadoresAtivo

logger = logging.getLogger(__name__)


class MarketDataService:
    """Serviço de obtenção de dados de mercado financeiro utilizando yfinance,
    com suporte a cache local, normalização de tickers da B3 (.SA) e tratamento de falhas.
    """

    CACHE_TTL_SECONDS = 300  # 5 minutos

    def __init__(self):
        self._quote_cache: Dict[str, Tuple[float, float]] = {}  # ticker -> (price, timestamp)
        self._history_cache: Dict[str, Tuple[pd.Series, float]] = {}
        self._info_cache: Dict[str, Tuple[dict, float]] = {}

    @staticmethod
    def normalize_ticker(ticker: str) -> str:
        """Converte tickers brasileiros para o formato do Yahoo Finance (ex: VALE3 -> VALE3.SA).
        Índices como ^BVSP são mantidos inalterados.
        """
        clean = ticker.strip().upper()
        if not clean:
            return ""
        if clean.startswith("^"):
            return clean
        if clean.endswith(".SA"):
            return clean
        # Se for um ticker de 5 ou 6 caracteres alfanuméricos típico da B3 (ex: PETR4, WEGE3, BOVA11, KNRI11)
        return f"{clean}.SA"

    def get_quote(self, ticker: str) -> Optional[float]:
        """Obtém a cotação mais recente de um ativo."""
        if not yf or not ticker:
            return None

        clean_ticker = ticker.strip().upper()
        # Verificar cache
        if clean_ticker in self._quote_cache:
            price, ts = self._quote_cache[clean_ticker]
            if time.time() - ts < self.CACHE_TTL_SECONDS:
                return price

        yf_ticker = self.normalize_ticker(clean_ticker)
        try:
            t = yf.Ticker(yf_ticker)
            # Tenta fast_info primeiro (mais rápido)
            price = None
            try:
                fast = t.fast_info
                price = getattr(fast, "last_price", None) or fast.get("lastPrice", None)
            except Exception:
                pass

            if price is None or price <= 0:
                hist = t.history(period="5d")
                if not hist.empty and "Close" in hist.columns:
                    price = float(hist["Close"].iloc[-1])

            if price is not None and price > 0:
                self._quote_cache[clean_ticker] = (float(price), time.time())
                return float(price)

        except Exception as e:
            logger.warning(f"Erro ao buscar cotação para {clean_ticker} ({yf_ticker}): {e}")

        return None

    def get_quotes_bulk(self, tickers: List[str]) -> Dict[str, float]:
        """Busca cotações para uma lista de tickers."""
        quotes = {}
        for t in set(tickers):
            if not t:
                continue
            q = self.get_quote(t)
            if q is not None:
                quotes[t.strip().upper()] = q
        return quotes

    def get_historical_data(
        self, ticker: str, start_date: datetime, end_date: Optional[datetime] = None
    ) -> pd.Series:
        """Retorna série de preços de fechamento diários para um ticker."""
        if not yf or not ticker:
            return pd.Series(dtype="float64")

        end_date = end_date or datetime.now()
        cache_key = f"{ticker}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"

        if cache_key in self._history_cache:
            series, ts = self._history_cache[cache_key]
            if time.time() - ts < self.CACHE_TTL_SECONDS * 2:
                return series

        yf_ticker = self.normalize_ticker(ticker)
        try:
            t = yf.Ticker(yf_ticker)
            # Adiciona 1 dia ao end_date para o yfinance ser inclusivo
            end_adjusted = end_date + timedelta(days=1)
            hist = t.history(start=start_date.strftime("%Y-%m-%d"), end=end_adjusted.strftime("%Y-%m-%d"))
            if not hist.empty and "Close" in hist.columns:
                series = hist["Close"].copy()
                # Remover fuso horário para facilitar comparações
                if hasattr(series.index, "tz_localize") and series.index.tz is not None:
                    series.index = series.index.tz_convert(None)
                self._history_cache[cache_key] = (series, time.time())
                return series
        except Exception as e:
            logger.warning(f"Erro ao obter histórico para {ticker}: {e}")

        return pd.Series(dtype="float64")

    def get_ibov_history(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.Series:
        """Retorna série histórica do índice Ibovespa (^BVSP)."""
        return self.get_historical_data("^BVSP", start_date, end_date)

    def get_indicators(self, ticker: str) -> Optional[IndicadoresAtivo]:
        """Obtém indicadores técnicos e fundamentalistas para um papel."""
        if not yf or not ticker:
            return None

        clean_ticker = ticker.strip().upper()
        yf_ticker = self.normalize_ticker(clean_ticker)

        try:
            t = yf.Ticker(yf_ticker)
            info = t.info or {}
            fast = getattr(t, "fast_info", {})

            cotacao = (
                info.get("currentPrice")
                or info.get("regularMarketPrice")
                or self.get_quote(clean_ticker)
                or 0.0
            )
            prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            variacao = 0.0
            if cotacao and prev_close and prev_close > 0:
                variacao = round(((cotacao / prev_close) - 1.0) * 100.0, 2)

            # Dividend Yield pode vir em decimal (0.065) ou percentual
            dy = info.get("dividendYield")
            if dy is not None:
                dy = dy * 100.0 if dy < 1.0 else dy

            return IndicadoresAtivo(
                ticker=clean_ticker,
                nome=info.get("shortName") or info.get("longName"),
                cotacao=round(float(cotacao), 2),
                variacao_dia_pct=variacao,
                fechamento_anterior=round(float(prev_close), 2) if prev_close else None,
                abertura=round(float(info.get("open", 0.0)), 2) if info.get("open") else None,
                minima_dia=round(float(info.get("dayLow", 0.0)), 2) if info.get("dayLow") else None,
                maxima_dia=round(float(info.get("dayHigh", 0.0)), 2) if info.get("dayHigh") else None,
                minima_52s=round(float(info.get("fiftyTwoWeekLow", 0.0)), 2) if info.get("fiftyTwoWeekLow") else None,
                maxima_52s=round(float(info.get("fiftyTwoWeekHigh", 0.0)), 2) if info.get("fiftyTwoWeekHigh") else None,
                pl=round(float(info.get("trailingPE", 0.0)), 2) if info.get("trailingPE") else None,
                dy=round(float(dy), 2) if dy is not None else None,
                pvp=round(float(info.get("priceToBook", 0.0)), 2) if info.get("priceToBook") else None,
                beta=round(float(info.get("beta", 0.0)), 2) if info.get("beta") else None,
                lpa=round(float(info.get("trailingEps", 0.0)), 2) if info.get("trailingEps") else None,
                setor=info.get("sector") or info.get("industry"),
            )

        except Exception as e:
            logger.warning(f"Erro ao obter indicadores de {clean_ticker}: {e}")
            return None

