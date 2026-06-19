from .base import BaseTipster, StockData


class TipsterG(BaseTipster):
    tipster_id = "G"
    tipster_name = "信用需給"

    def evaluate(self, data: StockData) -> dict:
        info = data.info
        criteria = []

        short_ratio = info.get("shortRatio")
        short_pct = info.get("shortPercentOfFloat")
        float_shares = info.get("floatShares")

        # yfinance provides limited margin/credit data for Japanese stocks.
        # We use shortRatio as a proxy where available.

        # 1. Credit ratio (信用倍率) - approximated from short data
        if short_ratio is not None:
            # shortRatio < 3 is healthy; > 5 means too much long bias
            ratio_pass = short_ratio <= 5.0
            criteria.append(self._criterion(
                "信用倍率",
                ratio_pass,
                f"ショートレシオ: {short_ratio:.2f}（5.0以下で通過）",
            ))
        else:
            ratio_pass = None
            criteria.append(self._criterion("信用倍率", False, "yfinanceから信用倍率データ未取得（日本株固有データのため）"))

        # 2. Short interest trend
        if short_pct is not None:
            short_decreasing = short_pct < 0.05
            criteria.append(self._criterion(
                "買い残推移",
                short_decreasing,
                f"ショート比率: {short_pct*100:.2f}%（5%未満で健全）",
            ))
        else:
            short_decreasing = None
            criteria.append(self._criterion("買い残推移", False, "データ未取得"))

        # 3. Reverse daily fee (逆日歩) - not available via yfinance
        criteria.append(self._criterion("逆日歩", False, "yfinanceでは逆日歩データ取得不可"))

        # 4. Lending ratio
        criteria.append(self._criterion("貸借倍率", False, "yfinanceでは日証金データ取得不可"))

        # 5. Turnover days (approximation using volume)
        vol_20 = data.volume_20d_avg
        if float_shares and vol_20 and vol_20 > 0:
            turnover_days = float_shares / vol_20
            turnover_pass = turnover_days < 200
            criteria.append(self._criterion(
                "回転日数",
                turnover_pass,
                f"浮動株{float_shares/1e6:.0f}M ÷ 20日平均出来高{vol_20:,.0f} = {turnover_days:.0f}日",
            ))
        else:
            turnover_pass = None
            criteria.append(self._criterion("回転日数", False, "データ未取得"))

        available_checks = [v for v in [ratio_pass, short_decreasing, turnover_pass] if v is not None]
        if not available_checks:
            return self._result(
                data, False, 0, criteria,
                "信用需給データはyfinanceから日本株では取得困難。日証金・東証データの手動入力が必要",
            )

        passed = sum(1 for v in available_checks if v)
        rec = passed >= 2 and (ratio_pass is None or ratio_pass is True)

        if rec:
            conf = 75
        else:
            conf = 0

        parts = []
        if short_ratio is not None:
            parts.append(f"ショートレシオ{short_ratio:.2f}")
        if short_pct is not None:
            parts.append(f"ショート比率{short_pct*100:.2f}%")
        parts.append("（日本株の信用残データはyfinanceでは限定的）")
        summary = "、".join(parts)

        return self._result(data, rec, conf, criteria, summary)
