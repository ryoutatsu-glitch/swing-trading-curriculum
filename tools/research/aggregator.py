from .config import MARK_THRESHOLDS


def assign_mark(recommendation_count: int) -> str:
    for mark in ["◎", "○", "▲"]:
        if recommendation_count >= MARK_THRESHOLDS[mark]:
            return mark
    return "△"


def aggregate_evaluations(evaluations: list[dict]) -> dict:
    recommendation_count = sum(1 for e in evaluations if e["recommendation"])
    total_confidence = sum(e["confidence"] for e in evaluations if e["recommendation"])
    mark = assign_mark(recommendation_count)

    return {
        "mark": mark,
        "recommendation_count": recommendation_count,
        "total_confidence": total_confidence,
        "evaluations": [
            {
                "tipster_id": e["tipster_id"],
                "tipster_name": _tipster_name(e["tipster_id"]),
                "recommendation": e["recommendation"],
                "confidence": e["confidence"],
                "summary": e["summary"],
            }
            for e in evaluations
        ],
    }


def _tipster_name(tipster_id: str) -> str:
    names = {
        "A": "トレンドテンプレート (Minervini)",
        "B": "CAN SLIMファンダメンタルズ (O'Neil)",
        "C": "イベントドリブン (CPAエッジ)",
        "D": "出来高分析",
        "E": "セクター分析",
        "F": "一目均衡表",
        "G": "信用需給",
    }
    return names.get(tipster_id, f"予想家{tipster_id}")
