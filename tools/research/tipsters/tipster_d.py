from .base import BaseTipster, StockData


class TipsterD(BaseTipster):
    tipster_id = "D"
    tipster_name = "出来高分析"

    def evaluate(self, data: StockData) -> dict:
        vol_20 = data.volume_20d_avg
        vol_50 = data.volume_50d_avg
        ratio = data.up_down_volume_ratio(20)
        h = data.hist

        if any(v is None for v in [vol_20, vol_50, ratio]) or h.empty:
            return self._result(data, False, 0, [], "データ不足のため評価不可")

        criteria = []

        # 1. Volume trend
        vol_trend = vol_20 > vol_50
        criteria.append(self._criterion(
            "出来高トレンド",
            vol_trend,
            f"20日平均{vol_20:,.0f} {'>' if vol_trend else '<'} 50日平均{vol_50:,.0f}",
        ))

        # 2. Up-day vs down-day volume
        vol_ratio_pass = ratio > 1.0
        criteria.append(self._criterion(
            "上昇日出来高 > 下落日出来高",
            vol_ratio_pass,
            f"上昇/下落出来高比: {ratio:.2f}（1.0超で通過）",
        ))

        # 3. Institutional accumulation (volume spike on up days)
        last_20 = h.tail(20)
        changes = last_20["Close"].diff()
        volumes = last_20["Volume"]
        avg_vol = volumes.mean()
        spike_up = ((changes > 0) & (volumes > avg_vol * 1.5)).any()
        criteria.append(self._criterion(
            "買い集め兆候",
            bool(spike_up),
            f"直近20日で出来高急増(1.5倍超)を伴う上昇日: {'あり' if spike_up else 'なし'}",
        ))

        # 4. Volume dry-up (contracting volatility pattern / VCP)
        last_10_vol = float(h["Volume"].tail(10).mean())
        prev_10_vol = float(h["Volume"].iloc[-20:-10].mean()) if len(h) >= 20 else last_10_vol
        dryup = last_10_vol < prev_10_vol * 0.8
        criteria.append(self._criterion(
            "出来高枯れ（VCP兆候）",
            dryup,
            f"直近10日平均{last_10_vol:,.0f} vs 前10日平均{prev_10_vol:,.0f}",
        ))

        # 5. Volume breakout
        recent_high = float(h["Close"].tail(5).max())
        prev_high = float(h["Close"].iloc[-25:-5].max()) if len(h) >= 25 else recent_high
        latest_vol = float(h["Volume"].iloc[-1])
        breakout = recent_high > prev_high and latest_vol > avg_vol * 1.3
        criteria.append(self._criterion(
            "出来高ブレイクアウト",
            breakout,
            f"直近高値{recent_high:,.0f} vs 前期高値{prev_high:,.0f}, 出来高{latest_vol:,.0f}",
        ))

        # Distribution check
        dist_days = ((changes < 0) & (volumes > avg_vol)).sum()
        distribution = dist_days >= 5
        criteria.append(self._criterion(
            "ディストリビューション兆候なし",
            not distribution,
            f"直近20日で出来高増加の下落日: {dist_days}日（5日以上で警戒）",
        ))

        accumulation = vol_ratio_pass and (spike_up or dryup)
        rec = accumulation and not distribution

        if rec:
            conf = 100 if breakout else 75
        else:
            conf = 0

        summary = (
            f"上昇/下落出来高比{ratio:.2f}, "
            f"20日平均出来高{vol_20:,.0f}, "
            f"{'アキュミュレーション' if accumulation else 'ディストリビューション'}パターン"
        )
        return self._result(data, rec, conf, criteria, summary)
