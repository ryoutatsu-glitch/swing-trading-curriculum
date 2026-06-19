import yfinance as yf

from .base import BaseTipster, StockData


class TipsterE(BaseTipster):
    tipster_id = "E"
    tipster_name = "セクター分析"

    def evaluate(self, data: StockData) -> dict:
        criteria = []
        info = data.info
        sector = info.get("sector", "不明")

        # Get TOPIX proxy (1306.T TOPIX ETF) for relative strength
        try:
            topix = yf.Ticker("1306.T")
            topix_hist = topix.history(period="6mo")
        except Exception:
            topix_hist = None

        stock_hist = data.hist

        if stock_hist.empty:
            return self._result(data, False, 0, [], "データ不足のため評価不可")

        # 1. Sector relative strength vs TOPIX
        if topix_hist is not None and not topix_hist.empty and len(stock_hist) >= 60:
            stock_3m_return = (float(stock_hist["Close"].iloc[-1]) / float(stock_hist["Close"].iloc[-60]) - 1) * 100
            topix_3m_return = (float(topix_hist["Close"].iloc[-1]) / float(topix_hist["Close"].iloc[-60]) - 1) * 100
            rs_pass = stock_3m_return > topix_3m_return
            criteria.append(self._criterion(
                "セクター相対強度",
                rs_pass,
                f"銘柄3ヶ月リターン{stock_3m_return:+.1f}% vs TOPIX{topix_3m_return:+.1f}%",
            ))
        else:
            rs_pass = False
            criteria.append(self._criterion("セクター相対強度", False, "TOPIX比較データ不足"))

        # 2. Rotation position (use recent momentum as proxy)
        if len(stock_hist) >= 20:
            momentum_1m = (float(stock_hist["Close"].iloc[-1]) / float(stock_hist["Close"].iloc[-20]) - 1) * 100
            rotation_pass = momentum_1m > 0
            criteria.append(self._criterion(
                "ローテーション位置",
                rotation_pass,
                f"直近1ヶ月リターン: {momentum_1m:+.1f}%（正で通過）",
            ))
        else:
            rotation_pass = False
            criteria.append(self._criterion("ローテーション位置", False, "データ不足"))

        # 3. Within-sector ranking (use beta and momentum as proxy)
        beta = info.get("beta")
        if beta is not None and rs_pass:
            rank_pass = True
            criteria.append(self._criterion(
                "セクター内順位",
                rank_pass,
                f"TOPIX超過リターン + ベータ{beta:.2f}でセクター上位と推定",
            ))
        else:
            rank_pass = False
            criteria.append(self._criterion(
                "セクター内順位",
                False,
                "TOPIXアンダーパフォームのためセクター上位とは言えない",
            ))

        # 4. Fund flow (use volume trend as proxy)
        vol_20 = data.volume_20d_avg
        vol_50 = data.volume_50d_avg
        if vol_20 is not None and vol_50 is not None:
            flow_pass = vol_20 > vol_50
            criteria.append(self._criterion(
                "資金フロー",
                flow_pass,
                f"20日平均出来高{vol_20:,.0f} {'>' if flow_pass else '<'} 50日平均{vol_50:,.0f}",
            ))
        else:
            flow_pass = False
            criteria.append(self._criterion("資金フロー", False, "データ不足"))

        rec = rs_pass and (rank_pass or rotation_pass)

        if rec:
            conf = 100 if rs_pass and rank_pass else 75
        else:
            conf = 0

        summary = f"セクター: {sector}。TOPIX対比{'アウトパフォーム' if rs_pass else 'アンダーパフォーム'}"
        return self._result(data, rec, conf, criteria, summary)
