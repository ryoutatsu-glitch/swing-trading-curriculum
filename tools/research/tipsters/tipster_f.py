from .base import BaseTipster, StockData


class TipsterF(BaseTipster):
    tipster_id = "F"
    tipster_name = "一目均衡表"

    def evaluate(self, data: StockData) -> dict:
        ichimoku = data.ichimoku()

        if ichimoku is None:
            return self._result(data, False, 0, [], "データ不足のため一目均衡表を計算不可（52日分必要）")

        criteria = []

        # 1. Price above cloud
        above_cloud = ichimoku["price_above_cloud"]
        criteria.append(self._criterion(
            "雲との位置関係",
            above_cloud,
            f"株価{ichimoku['price']:,.0f}円 vs 雲上限{ichimoku['cloud_top']:,.0f}円 "
            f"{'（雲の上）' if above_cloud else '（雲の下）'}",
        ))

        # 2. Three-line convergence (三役好転)
        tenkan_above = ichimoku["tenkan_above_kijun"]
        chikou_above = ichimoku["chikou_above_price"]
        sangyaku = above_cloud and tenkan_above and (chikou_above is True)
        conditions_met = sum([
            above_cloud,
            tenkan_above,
            chikou_above is True,
        ])

        detail_parts = []
        detail_parts.append(f"転換線{ichimoku['tenkan']:,.0f} {'>' if tenkan_above else '<'} 基準線{ichimoku['kijun']:,.0f}")
        if chikou_above is not None:
            detail_parts.append(f"遅行スパン{'上' if chikou_above else '下'}抜け")
        else:
            detail_parts.append("遅行スパン: データ不足")
        detail_parts.append(f"株価{'雲上' if above_cloud else '雲下'}")

        criteria.append(self._criterion(
            "三役好転",
            sangyaku,
            f"{conditions_met}/3条件成立。{', '.join(detail_parts)}",
        ))

        # 3. Cloud twist (not easily calculated without future data)
        criteria.append(self._criterion(
            "雲のねじれ",
            False,
            "先行スパンの将来交差は日足データからの推定に限界あり",
        ))

        # 4. Kijun direction
        kijun_rising = ichimoku.get("kijun_rising")
        if kijun_rising is not None:
            criteria.append(self._criterion(
                "基準線の方向",
                kijun_rising,
                f"基準線{ichimoku['kijun']:,.0f}円: {'上向き' if kijun_rising else '横ばいまたは下向き'}",
            ))
        else:
            kijun_rising = False
            criteria.append(self._criterion("基準線の方向", False, "データ不足"))

        if sangyaku:
            rec, conf = True, 100
        elif conditions_met >= 2:
            rec, conf = True, 75
        else:
            rec, conf = False, 0

        summary = (
            f"三役好転{'成立' if sangyaku else '未成立'}（{conditions_met}/3条件）。"
            f"転換線{ichimoku['tenkan']:,.0f}, 基準線{ichimoku['kijun']:,.0f}, "
            f"雲{ichimoku['cloud_bottom']:,.0f}〜{ichimoku['cloud_top']:,.0f}"
        )
        return self._result(data, rec, conf, criteria, summary)
