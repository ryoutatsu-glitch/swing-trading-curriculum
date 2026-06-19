# 予想家印方式リサーチツール — Claude Code ワークフロー

## 概要

TradingViewスクリーナーの結果を `watchlist.csv` に記入し、セッション内で銘柄評価を実行する。APIキー不要。

## ルーチン実行手順

ユーザーが「リサーチ実行」「銘柄を評価して」「/research」と言ったら、以下のワークフローを実行する：

### 1. ウォッチリスト読み込み

`watchlist.csv` を読み込み、対象銘柄リストを取得する。

### 2. 銘柄ごとの情報収集

各銘柄について WebSearch で以下の情報を収集する：

- 現在の株価、50日/150日/200日移動平均線、52週高値・安値
- EPS成長率、売上成長率、機関投資家保有比率
- 直近の決算・IR・適時開示
- 出来高推移、信用残、信用倍率
- セクター動向、一目均衡表の状態

検索クエリ例：
```
"{銘柄名} {証券コード} 株価 移動平均線 チャート テクニカル"
"{銘柄名} {証券コード} 決算 業績 EPS 売上"
"{銘柄名} {証券コード} 信用残 信用倍率 出来高"
```

### 3. 予想家評価（7人）

収集した情報をもとに、以下の7人の予想家の基準で評価する。
各予想家の詳細な評価基準は `docs/research-tool-spec.md` を参照。

| ID | 予想家 | 主な判定基準 |
|----|--------|-------------|
| A | トレンドテンプレート | 8項目チェック（MA順列、52週高値安値） |
| B | CAN SLIMファンダ | EPS成長率、機関保有、市場方向 |
| C | イベントドリブン | 決算サプライズ、上方修正、IR |
| D | 出来高分析 | アキュミュレーション/ディストリビューション |
| E | セクター分析 | セクター相対強度、ローテーション位置 |
| F | 一目均衡表 | 三役好転、雲との位置関係 |
| G | 信用需給 | 信用倍率、買い残推移、逆日歩 |

### 4. 印の決定

| 印 | 条件 |
|----|------|
| ◎ 本命 | 7人中5人以上が推奨 |
| ○ 対抗 | 7人中4人が推奨 |
| ▲ 単穴 | 7人中3人が推奨 |
| △ 連下 | 7人中2人以下が推奨 |

### 5. レポート生成

評価結果の JSON データを構築し、`tools/research/html_reporter.py` を使って HTML ダッシュボードを生成する。

```python
python3 -c "
from tools.research.html_reporter import save_html_report
import json, sys
data = json.loads(sys.stdin.read())
path = save_html_report(data)
print(f'Report saved: {path}')
" <<< '$JSON_DATA'
```

生成した HTML ファイルを `SendUserFile` でユーザーに送付する。

## ファイル構成

- `watchlist.csv` — 評価対象の銘柄リスト（ユーザーが更新）
- `docs/research-tool-spec.md` — 詳細仕様書
- `tools/research/html_reporter.py` — HTML レポート生成
- `tools/research/aggregator.py` — 印ロジック
- `output/` — 生成レポートの保存先
