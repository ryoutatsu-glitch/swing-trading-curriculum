from .base import BaseTipster, StockData


class TipsterB(BaseTipster):
    tipster_id = "B"
    tipster_name = "CAN SLIMファンダメンタルズ (O'Neil)"

    def evaluate(self, data: StockData) -> dict:
        info = data.info
        criteria = []
        details = {}

        # C - Current quarterly EPS growth
        eps_growth = info.get("earningsQuarterlyGrowth")
        if eps_growth is not None:
            c_pass = eps_growth >= 0.25
            details["c_growth"] = eps_growth
            criteria.append(self._criterion(
                "C - 当期EPS成長率",
                c_pass,
                f"四半期EPS成長率: {eps_growth*100:.1f}%（基準: +25%以上）",
            ))
        else:
            c_pass = False
            criteria.append(self._criterion("C - 当期EPS成長率", False, "データ未取得"))

        # A - Annual earnings growth
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        a_growth = earnings_growth if earnings_growth is not None else revenue_growth
        if a_growth is not None:
            a_pass = a_growth >= 0.25
            details["a_growth"] = a_growth
            criteria.append(self._criterion(
                "A - 年間EPS成長率",
                a_pass,
                f"年間成長率: {a_growth*100:.1f}%（基準: +25%以上）",
            ))
        else:
            a_pass = False
            criteria.append(self._criterion("A - 年間EPS成長率", False, "データ未取得"))

        # N - New products/management/highs
        p = data.price
        high = data.high_52w
        n_pass = False
        if p and high and high > 0:
            pct_of_high = p / high * 100
            n_pass = pct_of_high >= 90
            criteria.append(self._criterion(
                "N - 新高値",
                n_pass,
                f"52週高値の{pct_of_high:.1f}%（90%以上で通過）",
            ))
        else:
            criteria.append(self._criterion("N - 新高値", False, "データ未取得"))

        # S - Supply and demand (shares outstanding)
        shares = info.get("sharesOutstanding")
        s_pass = shares is not None and shares < 1_000_000_000
        criteria.append(self._criterion(
            "S - 需要と供給",
            s_pass,
            f"発行済株数: {shares/1e6:.0f}M株" if shares else "データ未取得",
        ))

        # L - Leader (relative strength)
        beta = info.get("beta")
        l_pass = beta is not None and beta >= 1.0
        criteria.append(self._criterion(
            "L - 主導銘柄",
            l_pass,
            f"ベータ: {beta:.2f}（1.0以上で通過）" if beta else "データ未取得",
        ))

        # I - Institutional ownership
        inst_pct = info.get("heldPercentInstitutions")
        i_pass = inst_pct is not None and inst_pct >= 0.10
        criteria.append(self._criterion(
            "I - 機関投資家の保有",
            i_pass,
            f"機関保有比率: {inst_pct*100:.1f}%" if inst_pct else "データ未取得",
        ))

        # M - Market direction (check if 200MA of index is rising)
        m_pass = True
        criteria.append(self._criterion(
            "M - 市場全体の方向",
            m_pass,
            "市場方向は個別チェックでは評価省略（通過扱い）",
        ))

        other_pass = sum(1 for c in criteria[2:] if c["passed"])
        rec = c_pass and a_pass and other_pass >= 3
        if rec:
            both_high = (details.get("c_growth", 0) >= 0.40 and details.get("a_growth", 0) >= 0.40)
            conf = 100 if both_high and other_pass >= 4 else 75
        else:
            conf = 0

        parts = []
        if eps_growth is not None:
            parts.append(f"四半期EPS{eps_growth*100:+.1f}%")
        if a_growth is not None:
            parts.append(f"年間{a_growth*100:+.1f}%")
        if inst_pct is not None:
            parts.append(f"機関保有{inst_pct*100:.0f}%")
        summary = "、".join(parts) if parts else "データ不足で評価困難"

        return self._result(data, rec, conf, criteria, summary)
