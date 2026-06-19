import argparse
import sys
import time
from datetime import datetime, timezone, timedelta

from .aggregator import aggregate_evaluations
from .html_reporter import save_html_report
from .reporter import generate_markdown_report, save_report
from .tipsters import TIPSTERS

JST = timezone(timedelta(hours=9))


def validate_ticker(ticker: str) -> bool:
    return ticker.isdigit() and len(ticker) == 4


def parse_input(args: list[str]) -> list[tuple[str, str]]:
    stocks = []
    for arg in args:
        if "," in arg:
            parts = arg.split(",", 1)
            ticker, name = parts[0].strip(), parts[1].strip()
        else:
            ticker = arg.strip()
            name = ""

        if not validate_ticker(ticker):
            print(f"⚠ 無効な証券コード: {ticker}（4桁の数字を入力してください）")
            continue

        stocks.append((ticker, name))

    seen = set()
    unique = []
    for ticker, name in stocks:
        if ticker not in seen:
            seen.add(ticker)
            unique.append((ticker, name))

    return unique[:10]


def evaluate_stock(ticker: str, company_name: str) -> dict:
    evaluations = []

    for tipster_id, tipster_cls in TIPSTERS.items():
        tipster = tipster_cls()
        label = f"{tipster.tipster_id} {tipster.tipster_name}"
        print(f"  📊 予想家{label} が評価中...")

        try:
            result = tipster.evaluate(ticker, company_name)
            evaluations.append(result)

            icon = "✅" if result["recommendation"] else "❌"
            print(f"     {icon} {result['summary']}")
        except Exception as e:
            print(f"     ⚠ エラー: {e}")
            evaluations.append({
                "ticker": ticker,
                "company_name": company_name,
                "tipster_id": tipster_id,
                "recommendation": False,
                "confidence": 0,
                "criteria_results": [],
                "summary": f"評価エラー: {e}",
                "data_sources": [],
            })

    aggregated = aggregate_evaluations(evaluations)
    return {
        "ticker": ticker,
        "company_name": company_name or ticker,
        **aggregated,
    }


def run(stocks: list[tuple[str, str]]) -> dict:
    print(f"\n🔍 {len(stocks)}銘柄のリサーチを開始します\n")
    print(f"   使用予想家: {', '.join(f'{k} {v.tipster_name}' for k, v in TIPSTERS.items())}")
    print()

    results = []
    for i, (ticker, name) in enumerate(stocks, 1):
        display = f"{ticker} {name}" if name else ticker
        print(f"[{i}/{len(stocks)}] {display}")

        stock_result = evaluate_stock(ticker, name)
        results.append(stock_result)
        print(f"  → 印: {stock_result['mark']}（{stock_result['recommendation_count']}/{len(TIPSTERS)}推奨）\n")

        if i < len(stocks):
            time.sleep(1)

    now = datetime.now(JST)
    report_data = {
        "generated_at": now.isoformat(),
        "stocks": results,
    }

    json_path, md_path = save_report(report_data)
    html_path = save_html_report(report_data)

    md_report = generate_markdown_report(report_data)
    print("=" * 60)
    print(md_report)
    print("=" * 60)
    print(f"\n📁 レポート保存先:")
    print(f"   JSON: {json_path}")
    print(f"   Markdown: {md_path}")
    print(f"   HTML: {html_path}")
    print(f"\n🌐 HTMLレポートをブラウザで開くには:")
    print(f"   start {html_path}")

    return report_data


def main():
    parser = argparse.ArgumentParser(
        description="予想家印方式リサーチツール - TradingViewスクリーナー銘柄の多角的評価",
    )
    parser.add_argument(
        "stocks",
        nargs="*",
        help="証券コード（例: 6758 または 6758,ソニーグループ）",
    )
    parser.add_argument(
        "--csv",
        type=str,
        help="銘柄リストのCSVファイルパス",
    )

    args = parser.parse_args()

    if args.csv:
        from pathlib import Path
        csv_path = Path(args.csv)
        if not csv_path.exists():
            print(f"❌ ファイルが見つかりません: {args.csv}")
            sys.exit(1)
        stock_args = [
            line.strip()
            for line in csv_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
    elif args.stocks:
        stock_args = args.stocks
    else:
        parser.print_help()
        print("\n使用例:")
        print("  python -m tools.research.main 6758,ソニーグループ 7203,トヨタ自動車")
        print("  python -m tools.research.main --csv stocks.csv")
        sys.exit(0)

    stocks = parse_input(stock_args)
    if not stocks:
        print("❌ 有効な銘柄が指定されていません")
        sys.exit(1)

    run(stocks)


if __name__ == "__main__":
    main()
