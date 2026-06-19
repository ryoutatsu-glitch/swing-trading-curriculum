from .base import BaseTipster, StockData


class TipsterC(BaseTipster):
    tipster_id = "C"
    tipster_name = "イベントドリブン (CPAエッジ)"

    def evaluate(self, data: StockData) -> dict:
        info = data.info
        criteria = []
        positive_count = 0
        negative_found = False

        # 1. Earnings surprise
        eps_growth = info.get("earningsQuarterlyGrowth")
        if eps_growth is not None:
            surprise = eps_growth > 0
            criteria.append(self._criterion(
                "決算サプライズ兆候",
                surprise,
                f"四半期EPS成長率: {eps_growth*100:+.1f}%（正ならポジティブ）",
            ))
            if surprise:
                positive_count += 1
        else:
            criteria.append(self._criterion("決算サプライズ兆候", False, "データ未取得"))

        # 2. Upward revision potential (revenue growth as proxy)
        rev_growth = info.get("revenueGrowth")
        if rev_growth is not None:
            revision = rev_growth > 0.05
            criteria.append(self._criterion(
                "上方修正の可能性",
                revision,
                f"売上成長率: {rev_growth*100:+.1f}%（+5%以上で通過）",
            ))
            if revision:
                positive_count += 1
        else:
            criteria.append(self._criterion("上方修正の可能性", False, "データ未取得"))

        # 3. Profit margin trend as proxy for IR/disclosure quality
        margin = info.get("profitMargins")
        if margin is not None:
            margin_ok = margin > 0.05
            criteria.append(self._criterion(
                "収益性",
                margin_ok,
                f"利益率: {margin*100:.1f}%（5%以上で通過）",
            ))
            if margin_ok:
                positive_count += 1
        else:
            criteria.append(self._criterion("収益性", False, "データ未取得"))

        # 4. Industry momentum (revenue growth as sector proxy)
        criteria.append(self._criterion(
            "業界動向",
            rev_growth is not None and rev_growth > 0,
            f"売上成長{rev_growth*100:+.1f}%で業界トレンドを推定" if rev_growth else "データ未取得",
        ))
        if rev_growth is not None and rev_growth > 0:
            positive_count += 1

        # Negative catalyst check: declining earnings
        if eps_growth is not None and eps_growth < -0.10:
            negative_found = True
            criteria.append(self._criterion(
                "ネガティブカタリスト",
                False,
                f"EPS{eps_growth*100:+.1f}%の大幅減益はネガティブ",
            ))

        has_surprise_or_revision = any(
            c["passed"] for c in criteria
            if c["criterion"] in ("決算サプライズ兆候", "上方修正の可能性")
        )
        rec = has_surprise_or_revision and not negative_found

        if rec:
            if positive_count >= 3 and not negative_found:
                conf = 100
            elif positive_count >= 1 and not negative_found:
                conf = 75
            else:
                conf = 50
        else:
            conf = 0

        parts = []
        if eps_growth is not None:
            parts.append(f"四半期EPS{eps_growth*100:+.1f}%")
        if rev_growth is not None:
            parts.append(f"売上{rev_growth*100:+.1f}%")
        if negative_found:
            parts.append("ネガティブカタリストあり")
        summary = "、".join(parts) if parts else "データ不足で評価困難"

        return self._result(data, rec, conf, criteria, summary)
