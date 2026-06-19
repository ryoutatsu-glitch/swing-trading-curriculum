import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>予想家印方式リサーチツール</title>
<style>
  :root {{
    --bg: #111318;
    --card-bg: #1A1D24;
    --card-border: #292D36;
    --surface: #22262F;
    --text-primary: #EEF0F4;
    --text-secondary: #99A1AF;
    --text-muted: #666D7A;
    --green: #32D788;
    --red: #EF505D;
    --gold: #FFC738;
    --blue: #478EFF;
    --purple: #9467F9;
    --orange: #FF9538;
    --accent: #468DFF;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Inter', 'Segoe UI', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
    background: var(--bg);
    color: var(--text-primary);
    min-height: 100vh;
  }}

  header {{
    background: rgba(21, 23, 29, 0.95);
    border-bottom: 1px solid var(--card-border);
    padding: 0 40px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
  }}

  .logo {{
    display: flex;
    align-items: baseline;
    gap: 12px;
  }}

  .logo h1 {{
    font-size: 22px;
    font-weight: 800;
    color: var(--gold);
    letter-spacing: -0.5px;
  }}

  .logo span {{
    font-size: 14px;
    color: var(--text-muted);
  }}

  .header-date {{
    font-size: 13px;
    color: var(--text-muted);
  }}

  main {{
    max-width: 1360px;
    margin: 0 auto;
    padding: 28px 40px 60px;
  }}

  .stats-bar {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1px;
    background: var(--card-border);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 28px;
  }}

  .stat {{
    background: var(--card-bg);
    padding: 20px 24px;
    text-align: center;
  }}

  .stat-value {{
    font-size: 28px;
    font-weight: 800;
    line-height: 1.2;
  }}

  .stat-label {{
    font-size: 11px;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
  }}

  .stock-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    margin-bottom: 20px;
    overflow: hidden;
    transition: border-color 0.2s;
  }}

  .stock-card:hover {{
    border-color: rgba(255, 199, 56, 0.3);
  }}

  .card-header {{
    display: flex;
    align-items: center;
    padding: 20px 28px;
    gap: 20px;
  }}

  .mark-badge {{
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    font-weight: 700;
    flex-shrink: 0;
  }}

  .mark-honmei {{ background: rgba(255, 199, 56, 0.12); color: var(--gold); }}
  .mark-taikou {{ background: rgba(50, 215, 136, 0.12); color: var(--green); }}
  .mark-tanana {{ background: rgba(71, 142, 255, 0.12); color: var(--blue); }}
  .mark-renge {{ background: rgba(102, 109, 122, 0.12); color: var(--text-muted); }}

  .stock-info {{
    flex: 1;
  }}

  .stock-ticker {{
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.5px;
  }}

  .stock-name {{
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 2px;
  }}

  .rec-badge {{
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
  }}

  .rec-honmei {{ background: rgba(255, 199, 56, 0.1); color: var(--gold); }}
  .rec-taikou {{ background: rgba(50, 215, 136, 0.1); color: var(--green); }}
  .rec-tanana {{ background: rgba(71, 142, 255, 0.1); color: var(--blue); }}
  .rec-renge {{ background: rgba(102, 109, 122, 0.1); color: var(--text-muted); }}

  .card-body {{
    border-top: 1px solid var(--card-border);
  }}

  .eval-table {{
    width: 100%;
    border-collapse: collapse;
  }}

  .eval-table th {{
    text-align: left;
    padding: 10px 28px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .eval-table td {{
    padding: 10px 28px;
    font-size: 13px;
    vertical-align: top;
  }}

  .eval-table tr:nth-child(even) {{
    background: rgba(34, 38, 47, 0.5);
  }}

  .eval-table tr:hover {{
    background: rgba(34, 38, 47, 0.8);
  }}

  .tipster-name {{
    color: var(--text-primary);
    font-weight: 500;
    white-space: nowrap;
  }}

  .tipster-id {{
    color: var(--text-muted);
    font-weight: 600;
    margin-right: 6px;
  }}

  .verdict-pass {{
    color: var(--green);
    font-weight: 700;
    font-size: 15px;
  }}

  .verdict-fail {{
    color: var(--red);
    font-weight: 700;
    font-size: 15px;
  }}

  .confidence {{
    color: var(--text-primary);
    font-weight: 600;
  }}

  .confidence-none {{
    color: var(--text-muted);
  }}

  .eval-summary {{
    color: var(--text-secondary);
    line-height: 1.5;
  }}

  .section-title {{
    font-size: 15px;
    font-weight: 700;
    color: var(--text-secondary);
    margin: 32px 0 16px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .section-title::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--card-border);
  }}

  .criteria-toggle {{
    background: none;
    border: 1px solid var(--card-border);
    color: var(--text-secondary);
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 11px;
    cursor: pointer;
    margin-left: auto;
    transition: all 0.2s;
  }}

  .criteria-toggle:hover {{
    border-color: var(--accent);
    color: var(--accent);
  }}

  .criteria-details {{
    display: none;
    padding: 0 28px 16px;
  }}

  .criteria-details.open {{
    display: block;
  }}

  .criteria-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 8px;
  }}

  .criteria-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    background: var(--surface);
    font-size: 12px;
  }}

  .criteria-icon {{
    flex-shrink: 0;
    margin-top: 1px;
  }}

  .criteria-pass {{ color: var(--green); }}
  .criteria-fail {{ color: var(--red); }}

  .criteria-text {{
    color: var(--text-secondary);
    line-height: 1.4;
  }}

  .criteria-text strong {{
    color: var(--text-primary);
    font-weight: 500;
  }}

  footer {{
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
    font-size: 12px;
    border-top: 1px solid var(--card-border);
  }}

  @media (max-width: 768px) {{
    header {{ padding: 0 20px; }}
    main {{ padding: 20px; }}
    .card-header {{ padding: 16px 20px; flex-wrap: wrap; }}
    .eval-table th, .eval-table td {{ padding: 8px 16px; }}
    .stats-bar {{ grid-template-columns: repeat(3, 1fr); }}
  }}
</style>
</head>
<body>

<header>
  <div class="logo">
    <h1>予想家印方式</h1>
    <span>リサーチツール</span>
  </div>
  <div class="header-date">{generated_at}</div>
</header>

<main>
  {stats_bar}
  {stock_cards}
</main>

<footer>
  予想家印方式リサーチツール — 投資判断はご自身の責任で行ってください
</footer>

<script>
function toggleCriteria(id) {{
  const el = document.getElementById(id);
  const btn = el.previousElementSibling.querySelector('.criteria-toggle');
  el.classList.toggle('open');
  btn.textContent = el.classList.contains('open') ? '詳細を隠す ▲' : '詳細を表示 ▼';
}}
</script>
</body>
</html>
"""


def _mark_class(mark: str) -> str:
    return {"◎": "honmei", "○": "taikou", "▲": "tanana", "△": "renge"}.get(mark, "renge")


def _build_stats_bar(report_data: dict) -> str:
    stocks = report_data.get("stocks", [])
    total = len(stocks)
    counts = {"◎": 0, "○": 0, "▲": 0, "△": 0}
    tipster_count = 0
    for s in stocks:
        counts[s["mark"]] = counts.get(s["mark"], 0) + 1
        tipster_count = max(tipster_count, len(s.get("evaluations", [])))

    stats = [
        ("分析銘柄数", str(total), "var(--text-primary)"),
        ("◎ 本命", str(counts["◎"]), "var(--gold)"),
        ("○ 対抗", str(counts["○"]), "var(--green)"),
        ("▲ 単穴", str(counts["▲"]), "var(--blue)"),
        ("△ 連下", str(counts["△"]), "var(--text-muted)"),
        ("使用予想家", f"{tipster_count}人", "var(--accent)"),
    ]

    items = []
    for label, value, color in stats:
        items.append(
            f'<div class="stat">'
            f'<div class="stat-value" style="color:{color}">{value}</div>'
            f'<div class="stat-label">{label}</div>'
            f'</div>'
        )
    return f'<div class="stats-bar">{"".join(items)}</div>'


def _build_stock_card(stock: dict, index: int) -> str:
    mark = stock["mark"]
    mc = _mark_class(mark)
    ticker = stock["ticker"]
    name = stock.get("company_name", "")
    rec_count = stock["recommendation_count"]
    total = len(stock.get("evaluations", []))

    rows = []
    for ev in stock.get("evaluations", []):
        rec = ev["recommendation"]
        verdict_cls = "verdict-pass" if rec else "verdict-fail"
        verdict_icon = "✓" if rec else "✗"
        conf = f'<span class="confidence">{ev["confidence"]}</span>' if rec else '<span class="confidence-none">-</span>'
        rows.append(
            f"<tr>"
            f'<td><span class="tipster-id">{ev["tipster_id"]}</span>'
            f'<span class="tipster-name">{ev.get("tipster_name", "")}</span></td>'
            f'<td><span class="{verdict_cls}">{verdict_icon}</span></td>'
            f"<td>{conf}</td>"
            f'<td class="eval-summary">{ev["summary"]}</td>'
            f"</tr>"
        )

    criteria_html = ""
    if "criteria_results" in stock.get("evaluations", [{}])[0] if stock.get("evaluations") else False:
        pass

    card_id = f"criteria-{index}"

    return (
        f'<div class="stock-card">'
        f'<div class="card-header">'
        f'<div class="mark-badge mark-{mc}">{mark}</div>'
        f'<div class="stock-info">'
        f'<div class="stock-ticker">{ticker}</div>'
        f'<div class="stock-name">{name}</div>'
        f"</div>"
        f'<div class="rec-badge rec-{mc}">{rec_count}/{total} 推奨</div>'
        f"</div>"
        f'<div class="card-body">'
        f'<table class="eval-table">'
        f"<thead><tr><th>予想家</th><th>判定</th><th>確信度</th><th>要約</th></tr></thead>"
        f'<tbody>{"".join(rows)}</tbody>'
        f"</table>"
        f"</div>"
        f"</div>"
    )


def generate_html_report(report_data: dict) -> str:
    stats_bar = _build_stats_bar(report_data)

    mark_order = {"◎": 0, "○": 1, "▲": 2, "△": 3}
    sorted_stocks = sorted(
        report_data.get("stocks", []),
        key=lambda s: (mark_order.get(s["mark"], 9), -s.get("total_confidence", 0)),
    )

    cards = []
    current_mark = None
    mark_labels = {"◎": "◎ 本命", "○": "○ 対抗", "▲": "▲ 単穴", "△": "△ 連下"}

    for i, stock in enumerate(sorted_stocks):
        if stock["mark"] != current_mark:
            current_mark = stock["mark"]
            label = mark_labels.get(current_mark, current_mark)
            cards.append(f'<div class="section-title">{label}</div>')

        cards.append(_build_stock_card(stock, i))

    generated_at = report_data.get("generated_at", datetime.now(JST).isoformat())
    if "T" in generated_at:
        try:
            dt = datetime.fromisoformat(generated_at)
            generated_at = dt.strftime("%Y-%m-%d %H:%M JST")
        except ValueError:
            pass

    return HTML_TEMPLATE.format(
        generated_at=generated_at,
        stats_bar=stats_bar,
        stock_cards="\n".join(cards),
    )


def save_html_report(report_data: dict, output_dir: str = "output") -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    now = datetime.now(JST)
    date_str = now.strftime("%Y-%m-%d_%H%M")

    html_content = generate_html_report(report_data)
    html_path = output_path / f"{date_str}_report.html"
    html_path.write_text(html_content, encoding="utf-8")

    return str(html_path)
