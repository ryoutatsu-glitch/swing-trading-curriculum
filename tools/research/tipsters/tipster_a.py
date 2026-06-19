from .base import BaseTipster, StockData


class TipsterA(BaseTipster):
    tipster_id = "A"
    tipster_name = "トレンドテンプレート (Minervini)"

    def evaluate(self, data: StockData) -> dict:
        p = data.price
        ma50 = data.ma50
        ma150 = data.ma150
        ma200 = data.ma200
        ma200_prev = data.ma200_1m_ago
        high = data.high_52w
        low = data.low_52w

        if any(v is None for v in [p, ma50, ma150, ma200, high, low]):
            return self._result(data, False, 0, [], "データ不足のため評価不可")

        pct_above_low = (p - low) / low * 100
        pct_of_high = p / high * 100

        checks = [
            ("1. 株価 > 200日MA", p > ma200,
             f"株価{p:,.0f}円 {'>' if p > ma200 else '<'} 200日MA{ma200:,.0f}円"),
            ("2. 200日MAが上昇トレンド",
             ma200_prev is not None and ma200 > ma200_prev,
             f"200日MA{ma200:,.0f}円 → 1ヶ月前{ma200_prev:,.0f}円" if ma200_prev else "データ不足"),
            ("3. 株価 > 150日MA", p > ma150,
             f"株価{p:,.0f}円 {'>' if p > ma150 else '<'} 150日MA{ma150:,.0f}円"),
            ("4. 150日MA > 200日MA", ma150 > ma200,
             f"150日MA{ma150:,.0f}円 {'>' if ma150 > ma200 else '<'} 200日MA{ma200:,.0f}円"),
            ("5. 50日MA > 150日MA・200日MA", ma50 > ma150 and ma50 > ma200,
             f"50日MA{ma50:,.0f}円 vs 150日MA{ma150:,.0f}円, 200日MA{ma200:,.0f}円"),
            ("6. 株価 > 50日MA", p > ma50,
             f"株価{p:,.0f}円 {'>' if p > ma50 else '<'} 50日MA{ma50:,.0f}円"),
            ("7. 52週安値+25%以上", pct_above_low >= 25,
             f"安値{low:,.0f}円から+{pct_above_low:.1f}%（基準: +25%以上）"),
            ("8. 52週高値の75%以内", pct_of_high >= 75,
             f"高値{high:,.0f}円の{pct_of_high:.1f}%（基準: 75%以上）"),
        ]

        criteria = [self._criterion(name, passed, detail) for name, passed, detail in checks]
        passed_count = sum(1 for _, p, _ in checks if p)

        if passed_count >= 8:
            rec, conf = True, 100
        elif passed_count >= 7:
            rec, conf = True, 75
        else:
            rec, conf = False, 0

        summary = f"8項目中{passed_count}項目通過。株価{p:,.0f}円, 50MA{ma50:,.0f}, 150MA{ma150:,.0f}, 200MA{ma200:,.0f}"
        return self._result(data, rec, conf, criteria, summary)
