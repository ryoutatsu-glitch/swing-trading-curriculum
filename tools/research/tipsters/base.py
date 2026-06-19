from abc import ABC, abstractmethod

import yfinance as yf
import pandas as pd


class StockData:
    """yfinance から取得した株価データを保持するクラス"""

    def __init__(self, ticker: str, company_name: str):
        self.ticker = ticker
        self.company_name = company_name
        self.yf_ticker = f"{ticker}.T"
        self._stock = yf.Ticker(self.yf_ticker)
        self._hist = None
        self._info = None
        self._financials = None
        self._quarterly_financials = None

    @property
    def hist(self) -> pd.DataFrame:
        if self._hist is None:
            self._hist = self._stock.history(period="1y")
        return self._hist

    @property
    def info(self) -> dict:
        if self._info is None:
            try:
                self._info = self._stock.info
            except Exception:
                self._info = {}
        return self._info

    @property
    def financials(self) -> pd.DataFrame:
        if self._financials is None:
            try:
                self._financials = self._stock.financials
            except Exception:
                self._financials = pd.DataFrame()
        return self._financials

    @property
    def quarterly_financials(self) -> pd.DataFrame:
        if self._quarterly_financials is None:
            try:
                self._quarterly_financials = self._stock.quarterly_financials
            except Exception:
                self._quarterly_financials = pd.DataFrame()
        return self._quarterly_financials

    @property
    def price(self) -> float | None:
        if self.hist.empty:
            return None
        return float(self.hist["Close"].iloc[-1])

    @property
    def ma50(self) -> float | None:
        if len(self.hist) < 50:
            return None
        return float(self.hist["Close"].rolling(50).mean().iloc[-1])

    @property
    def ma150(self) -> float | None:
        if len(self.hist) < 150:
            return None
        return float(self.hist["Close"].rolling(150).mean().iloc[-1])

    @property
    def ma200(self) -> float | None:
        if len(self.hist) < 200:
            return None
        return float(self.hist["Close"].rolling(200).mean().iloc[-1])

    @property
    def ma200_1m_ago(self) -> float | None:
        if len(self.hist) < 222:
            return None
        return float(self.hist["Close"].rolling(200).mean().iloc[-22])

    @property
    def high_52w(self) -> float | None:
        if self.hist.empty:
            return None
        return float(self.hist["Close"].max())

    @property
    def low_52w(self) -> float | None:
        if self.hist.empty:
            return None
        return float(self.hist["Close"].min())

    @property
    def volume_20d_avg(self) -> float | None:
        if len(self.hist) < 20:
            return None
        return float(self.hist["Volume"].rolling(20).mean().iloc[-1])

    @property
    def volume_50d_avg(self) -> float | None:
        if len(self.hist) < 50:
            return None
        return float(self.hist["Volume"].rolling(50).mean().iloc[-1])

    def up_down_volume_ratio(self, days: int = 20) -> float | None:
        if len(self.hist) < days + 1:
            return None
        recent = self.hist.tail(days + 1)
        changes = recent["Close"].diff().iloc[1:]
        volumes = recent["Volume"].iloc[1:]
        up_vol = float(volumes[changes > 0].sum())
        down_vol = float(volumes[changes < 0].sum())
        if down_vol == 0:
            return float("inf") if up_vol > 0 else 1.0
        return up_vol / down_vol

    def ichimoku(self) -> dict | None:
        h = self.hist
        if len(h) < 52:
            return None
        high = h["High"]
        low = h["Low"]
        close = h["Close"]

        tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_a = ((tenkan + kijun) / 2).shift(26)
        senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        chikou = close.shift(-26)

        latest_price = float(close.iloc[-1])
        latest_tenkan = float(tenkan.iloc[-1])
        latest_kijun = float(kijun.iloc[-1])
        cloud_top = float(max(senkou_a.iloc[-1], senkou_b.iloc[-1]))
        cloud_bottom = float(min(senkou_a.iloc[-1], senkou_b.iloc[-1]))
        chikou_val = float(chikou.iloc[-27]) if len(chikou) > 27 else None
        chikou_ref_price = float(close.iloc[-27]) if len(close) > 27 else None

        return {
            "tenkan": latest_tenkan,
            "kijun": latest_kijun,
            "cloud_top": cloud_top,
            "cloud_bottom": cloud_bottom,
            "price": latest_price,
            "chikou": chikou_val,
            "chikou_ref_price": chikou_ref_price,
            "price_above_cloud": latest_price > cloud_top,
            "tenkan_above_kijun": latest_tenkan > latest_kijun,
            "chikou_above_price": (chikou_val > chikou_ref_price) if chikou_val and chikou_ref_price else None,
            "kijun_rising": float(kijun.iloc[-1]) > float(kijun.iloc[-5]) if len(kijun) >= 5 else None,
        }


class BaseTipster(ABC):
    tipster_id: str = ""
    tipster_name: str = ""

    @abstractmethod
    def evaluate(self, data: StockData) -> dict:
        ...

    def _result(
        self,
        data: StockData,
        recommendation: bool,
        confidence: int,
        criteria_results: list[dict],
        summary: str,
    ) -> dict:
        return {
            "ticker": data.ticker,
            "company_name": data.company_name,
            "tipster_id": self.tipster_id,
            "recommendation": recommendation,
            "confidence": confidence,
            "criteria_results": criteria_results,
            "summary": summary,
            "data_sources": [f"yfinance:{data.yf_ticker}"],
        }

    @staticmethod
    def _criterion(name: str, passed: bool, detail: str) -> dict:
        return {"criterion": name, "passed": passed, "detail": detail}
