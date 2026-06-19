import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))


def generate_markdown_report(report_data: dict) -> str:
    lines = [
        "# 予想家印レポート",
        f"**生成日時**: {report_data['generated_at']}",
        "",
    ]

    mark_groups = {"◎": [], "○": [], "▲": [], "△": []}
    for stock in report_data["stocks"]:
        mark_groups[stock["mark"]].append(stock)

    mark_labels = {
        "◎": "◎ 本命",
        "○": "○ 対抗",
        "▲": "▲ 単穴",
        "△": "△ 連下",
    }

    for mark, label in mark_labels.items():
        stocks = mark_groups[mark]
        if not stocks:
            continue

        lines.append(f"## {label}")
        lines.append("")

        for stock in stocks:
            rec = stock["recommendation_count"]
            total = len(stock["evaluations"])
            lines.append(f"### {stock['ticker']} {stock['company_name']} ({rec}/{total}推奨)")
            lines.append("")
            lines.append("| 予想家 | 判定 | 確信度 | 要約 |")
            lines.append("|--------|------|--------|------|")

            for ev in stock["evaluations"]:
                icon = "✅" if ev["recommendation"] else "❌"
                conf = str(ev["confidence"]) if ev["recommendation"] else "-"
                lines.append(
                    f"| {ev['tipster_id']} {ev['tipster_name']} "
                    f"| {icon} | {conf} | {ev['summary']} |"
                )

            lines.append("")

    return "\n".join(lines)


def save_report(report_data: dict, output_dir: str = "output") -> tuple[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    now = datetime.now(JST)
    date_str = now.strftime("%Y-%m-%d_%H%M")

    json_path = output_path / f"{date_str}_report.json"
    json_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")

    md_content = generate_markdown_report(report_data)
    md_path = output_path / f"{date_str}_report.md"
    md_path.write_text(md_content, encoding="utf-8")

    return str(json_path), str(md_path)
