予想家印方式リサーチツール 仕様書
1. 概要
TradingViewスクリーナーが出力した銘柄コードリストに対し、7人の「予想家」（各々が異なる投資手法を代表）がClaude APIのweb_search機能で情報を収集・評価し、競馬の予想紙方式（◎○▲△）でランキングレポートを生成するツール。
位置づけ
```
スクリーニング層（TradingView） → 深掘りリサーチ層（本ツール） → 判断層（人間）
```
本ツールは「深掘りリサーチ層」を担う。データ取得・スクリーニングは既存プロツールに任せ、自作するのはリサーチロジックのみという設計思想に従う。
---
2. システムアーキテクチャ
データフロー
```
[入力]
  TradingView Minervini Trend Template Screener
  → 銘柄コードリスト（CSV / 手動入力）
       ↓
[情報収集]
  Claude API web_search (web_search_20260209)
  → 各銘柄の財務データ・ニュース・テクニカル情報
       ↓
[評価]
  7人の予想家（個別プロンプト）
  → 各予想家が「推奨 / 非推奨」+ 確信度 + 根拠を返す
       ↓
[集計]
  印ロジック（推奨数 → ◎○▲△）
       ↓
[出力]
  印付きランキングレポート（Markdown / JSON）
```
技術スタック
項目	選定	理由
言語	Python 3.11+	ユーザー既存スキル、Claude SDK充実
SDK	`anthropic` (Python)	公式SDK、web_search対応
モデル	`claude-opus-4-8`	最高精度、adaptive thinking対応
情報収集	`web_search_20260209`	動的フィルタリング対応のサーバーサイドツール
URL取得	`web_fetch_20260209`	特定ページの詳細取得用
出力形式	Structured Outputs (`output_config`)	後続処理（ジャーナル連携）のため型安全
実行環境	ローカル（CLI）	シンプル、API キーのみで動作
---
3. 予想家の詳細仕様
3.1 予想家A: トレンドテンプレート (Minervini)
手法: SEPA / Trend Template / VCP
評価項目（8項目チェック）:
#	項目	判定基準
1	現在の株価 > 200日移動平均線	Stage 2の最低条件
2	200日移動平均線が上昇トレンド	少なくとも1ヶ月間上昇
3	現在の株価 > 150日移動平均線	中期トレンド確認
4	150日移動平均線 > 200日移動平均線	移動平均線の順列
5	50日移動平均線 > 150日・200日移動平均線	短期トレンドの優位性
6	現在の株価 > 50日移動平均線	直近の強さ
7	株価が52週安値の25%以上上	底値圏でないことの確認
8	株価が52週高値の75%以内	新高値圏に近い位置
推奨判定: 8項目中7項目以上を通過で「推奨」
確信度ロジック:
8/8通過 → 確信度 100
7/8通過 → 確信度 75
6/8以下 → 非推奨
web_search クエリ例:
```
"{銘柄名} {証券コード} 株価 移動平均線 50日 150日 200日 52週高値安値"
```
---
3.2 予想家B: CAN SLIMファンダメンタルズ (O'Neil)
手法: CAN SLIM
評価項目:
項目	判定基準	重み
C - 当期EPS成長率	前年同期比 +25%以上	高
A - 年間EPS成長率	過去3年間 +25%/年以上	高
N - 新製品/新経営/新高値	何らかの「新」要素があるか	中
S - 需要と供給	発行済株数が適正（大きすぎない）	低
L - 主導銘柄	セクター内の相対強度上位か	中
I - 機関投資家の保有	機関保有比率の推移（増加傾向が望ましい）	中
M - 市場全体の方向	日経平均・TOPIXのトレンド	低
推奨判定: C, A が両方基準を満たし、かつ残り5項目中3項目以上を通過で「推奨」
確信度ロジック:
C, A 両方 +40%以上 & 他4項目通過 → 確信度 100
C, A 両方 +25%以上 & 他3項目通過 → 確信度 75
C, A いずれか未達 → 非推奨
web_search クエリ例:
```
"{銘柄名} {証券コード} EPS 四半期業績 売上成長率 前年比"
"{銘柄名} {証券コード} 機関投資家 保有比率 大株主"
```
---
3.3 予想家C: イベントドリブン（CPAエッジ）
手法: 決算・IR・制度変更からのカタリスト分析
評価項目:
項目	判定基準	重み
決算サプライズ兆候	直近四半期でコンセンサス上振れ実績があるか	高
上方修正の可能性	進捗率が過去パターンから乖離（上振れ方向）	高
IR・適時開示	直近1ヶ月のIR内容にポジティブカタリストがあるか	高
業界動向	業界全体にポジティブな構造変化があるか	中
税制・規制変更	該当セクターに影響する制度変更の有無	中（CPA固有）
会計方針変更	収益認識変更など、見かけの変化と実質を区別	低（CPA固有）
推奨判定: 「決算サプライズ兆候」または「上方修正の可能性」のいずれかが該当し、かつネガティブカタリストが存在しないこと
確信度ロジック:
複数のポジティブカタリスト + ネガティブなし → 確信度 100
単一のポジティブカタリスト + ネガティブなし → 確信度 75
ポジティブ/ネガティブ混在 → 確信度 50（推奨だが注意喚起）
web_search クエリ例:
```
"{銘柄名} {証券コード} 決算 業績修正 上方修正 2026"
"{銘柄名} {証券コード} 適時開示 IR ニュース"
"{銘柄名} 業界 規制 税制改正"
```
設計意図: ユーザーのCPA背景が最もエッジになる予想家。将来的にはプロンプトにCPA視点の分析指示を追加してカスタマイズ可能。
---
3.4 予想家D: 出来高分析
手法: アキュミュレーション/ディストリビューション判定
評価項目:
項目	判定基準
出来高トレンド	直近20日間の平均出来高が50日平均を上回っているか
価格上昇日の出来高	上昇日の出来高 > 下落日の出来高（過去20日間）
機関の買い集め兆候	出来高急増を伴う上昇日が直近に存在するか
出来高枯れ	ベース形成中に出来高が減少しているか（VCPの兆候）
出来高ブレイクアウト	直近にレジスタンス突破＋出来高急増があったか
推奨判定: 「アキュミュレーション（買い集め）」パターンが確認でき、「ディストリビューション（売り抜け）」兆候がないこと
確信度ロジック:
出来高ブレイクアウト確認 → 確信度 100
アキュミュレーション兆候あり → 確信度 75
判断困難 → 非推奨
web_search クエリ例:
```
"{銘柄名} {証券コード} 出来高 推移 売買高"
"{銘柄名} {証券コード} 株探 チャート"
```
---
3.5 予想家E: セクター分析
手法: セクターローテーション・相対強度
評価項目:
項目	判定基準
セクター相対強度	該当セクターの対TOPIX相対パフォーマンスが上昇トレンドか
ローテーション位置	現在の景気サイクルで有利なセクターか
セクター内順位	銘柄がセクター内で上位パフォーマーか
資金フロー	セクターETFへの資金流入が増加傾向か
推奨判定: セクター相対強度が上昇トレンド、かつセクター内で上位パフォーマー
確信度ロジック:
セクター強 & 銘柄もセクター内上位 → 確信度 100
セクター強だが銘柄は中位 → 確信度 75
セクター弱 → 非推奨
web_search クエリ例:
```
"{セクター名} セクター 相対強度 TOPIX 2026"
"東証 業種別 パフォーマンス ランキング"
```
---
3.6 予想家F: 一目均衡表
手法: 一目均衡表（日本株固有のテクニカル指標）
評価項目:
項目	判定基準
雲との位置関係	株価が雲の上にあるか
三役好転	転換線>基準線、遅行スパン>株価、株価>雲 の3条件が揃っているか
雲のねじれ	今後26日以内に雲のねじれ（トレンド転換点）があるか
基準線の方向	基準線が上向きか
推奨判定: 三役好転が成立、または2条件成立かつ残り1条件が近日中に成立見込み
確信度ロジック:
三役好転完全成立 → 確信度 100
2条件成立 + 残り1条件が近い → 確信度 75
2条件未満 → 非推奨
web_search クエリ例:
```
"{銘柄名} {証券コード} 一目均衡表 三役好転"
"{銘柄名} {証券コード} テクニカル分析 チャート"
```
---
3.7 予想家G: 信用需給
手法: 信用取引データからの需給分析
評価項目:
項目	判定基準
信用倍率	1.0倍以下（売り残 > 買い残 = 将来の買い戻し圧力）
買い残推移	減少傾向（将来の売り圧力が軽減）
逆日歩	発生中なら空売りコストが高く、買い戻し圧力あり
貸借倍率	日証金ベースでの需給状況
回転日数	信用買い残 ÷ 1日平均出来高（短いほど健全）
推奨判定: 信用倍率が健全（5.0倍以下）で、買い残が減少傾向、または逆日歩が発生中
確信度ロジック:
信用倍率 < 1.0 + 逆日歩あり → 確信度 100（踏み上げ期待）
信用倍率 1.0〜3.0 + 買い残減少 → 確信度 75
信用倍率 > 5.0 → 非推奨（将来の売り圧力が大きい）
web_search クエリ例:
```
"{銘柄名} {証券コード} 信用残 信用倍率 買い残 売り残"
"{銘柄名} {証券コード} 逆日歩 貸借"
```
---
4. 印（マーク）ロジック
集計ルール
各予想家が「推奨」を出した数に応じて印を決定する:
印	意味	条件	行動指針
◎（本命）	複数の手法が強く支持	7人中5人以上が推奨	エントリー候補。フルサイズポジション検討
○（対抗）	多角的に見て有望	7人中4人が推奨	エントリー候補。標準サイズポジション
▲（単穴）	部分的に有望だが懸念あり	7人中3人が推奨	ウォッチリスト。条件改善待ち
△（連下）	現時点では見送り	7人中2人以下が推奨	見送り
確信度による加重（将来拡張）
基本ロジックは単純な推奨数カウント。将来的には確信度で加重する拡張を検討:
```
加重スコア = Σ(推奨した予想家の確信度) / 700
```
---
5. ゴチ方式（予想家の淘汰・進化）
成績追跡
各予想家について以下を個別に記録する:
指標	計算方法
推奨勝率	推奨銘柄のうち利益が出たトレードの割合
平均R倍数	推奨銘柄の平均利益（1Rリスク単位）
期待値	(勝率 × 平均利益) - ((1-勝率) × 平均損失)
推奨的中率	◎○の銘柄がエントリーされた率（参考）
淘汰ルール
評価開始: 最低20トレード（推奨した銘柄がエントリーされたもの）を経過後
退場条件: 期待値がマイナス、かつ推奨勝率が40%未満
猶予: 退場判定前に10トレードの猶予期間（改善機会）
新規参戦: 新しい投資手法を学んだら、新予想家としてプロンプトを追加可能
設計意図
ユーザーにとって最適な予想家の組み合わせは事前にわからない
実際のトレードデータに基づいて自然淘汰させることで、アンサンブルが個人の強みに最適化される
成績データはトレードジャーナル（別ツール）から供給
---
6. Claude API 実装仕様
6.1 API呼び出しパターン
1銘柄あたり7回の予想家評価を実行する。各予想家は1回のAPI呼び出し（web_search付き）で完結する。
```python
import anthropic

client = anthropic.Anthropic()

def evaluate_stock(ticker: str, company_name: str, tipster_prompt: str) -> dict:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        tools=[
            {"type": "web_search_20260209"},
            {"type": "web_fetch_20260209"},
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": TIPSTER_RESULT_SCHEMA,
            }
        },
        messages=[
            {
                "role": "user",
                "content": tipster_prompt.format(
                    ticker=ticker,
                    company_name=company_name,
                ),
            }
        ],
    )
    return response
```
6.2 出力スキーマ（Structured Outputs）
```json
{
  "name": "tipster_evaluation",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "証券コード"
      },
      "company_name": {
        "type": "string",
        "description": "企業名"
      },
      "tipster_id": {
        "type": "string",
        "description": "予想家ID（A〜G）"
      },
      "recommendation": {
        "type": "boolean",
        "description": "推奨するか否か"
      },
      "confidence": {
        "type": "integer",
        "description": "確信度（0-100）"
      },
      "criteria_results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "criterion": {
              "type": "string",
              "description": "評価項目名"
            },
            "passed": {
              "type": "boolean",
              "description": "基準を通過したか"
            },
            "detail": {
              "type": "string",
              "description": "判定根拠の詳細"
            }
          },
          "required": ["criterion", "passed", "detail"],
          "additionalProperties": false
        },
        "description": "各評価項目の結果"
      },
      "summary": {
        "type": "string",
        "description": "評価の要約（1-2文）"
      },
      "data_sources": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "情報取得元のURL一覧"
      }
    },
    "required": [
      "ticker",
      "company_name",
      "tipster_id",
      "recommendation",
      "confidence",
      "criteria_results",
      "summary",
      "data_sources"
    ],
    "additionalProperties": false
  }
}
```
6.3 最終出力スキーマ（銘柄レポート）
```json
{
  "name": "stock_report",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "generated_at": {
        "type": "string",
        "description": "レポート生成日時（ISO 8601）"
      },
      "stocks": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "ticker": { "type": "string" },
            "company_name": { "type": "string" },
            "mark": {
              "type": "string",
              "enum": ["◎", "○", "▲", "△"],
              "description": "印"
            },
            "recommendation_count": {
              "type": "integer",
              "description": "推奨した予想家の数（0-7）"
            },
            "total_confidence": {
              "type": "integer",
              "description": "推奨した予想家の確信度合計"
            },
            "evaluations": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "tipster_id": { "type": "string" },
                  "tipster_name": { "type": "string" },
                  "recommendation": { "type": "boolean" },
                  "confidence": { "type": "integer" },
                  "summary": { "type": "string" }
                },
                "required": [
                  "tipster_id",
                  "tipster_name",
                  "recommendation",
                  "confidence",
                  "summary"
                ],
                "additionalProperties": false
              }
            }
          },
          "required": [
            "ticker",
            "company_name",
            "mark",
            "recommendation_count",
            "total_confidence",
            "evaluations"
          ],
          "additionalProperties": false
        }
      }
    },
    "required": ["generated_at", "stocks"],
    "additionalProperties": false
  }
}
```
---
7. 入力仕様
入力形式
TradingViewスクリーナーの出力を以下の形式で受け付ける:
```
# CSV形式（推奨）
6758,ソニーグループ
7203,トヨタ自動車
9984,ソフトバンクグループ

# またはコマンドライン引数
python research_tool.py 6758 7203 9984

# または対話モード
python research_tool.py --interactive
```
入力バリデーション
証券コード: 4桁の数字（東証）
1回の実行で最大10銘柄（API コスト管理）
重複排除
---
8. 出力仕様
Markdownレポート（人間向け）
```markdown
# 予想家印レポート
**生成日時**: 2026-06-19 15:30:00 JST

## ◎ 本命
### 6758 ソニーグループ (5/7推奨)
| 予想家 | 判定 | 確信度 | 要約 |
|--------|------|--------|------|
| A トレンドテンプレート | ✅ | 100 | 8項目全通過。Stage 2中盤 |
| B CAN SLIMファンダ | ✅ | 75 | EPS +32%、売上 +18% |
| C イベントドリブン | ✅ | 75 | PS5 Pro効果で上方修正期待 |
| D 出来高分析 | ✅ | 75 | 出来高増加傾向、買い集め兆候 |
| E セクター分析 | ✅ | 100 | 電機セクター相対強度上昇中 |
| F 一目均衡表 | ❌ | - | 三役好転未成立（遅行スパン未達） |
| G 信用需給 | ❌ | - | 信用倍率 6.2倍（買い残重い） |

## ○ 対抗
...

## ▲ 単穴
...

## △ 連下
...
```
JSONレポート（トレードジャーナル連携用）
前述の`stock_report`スキーマに従ったJSON出力を `output/{date}_report.json` に保存。
---
9. コスト見積もり
1銘柄あたり
項目	見積もり
予想家数	7回
入力トークン/回	~2,000（プロンプト） + ~5,000（web_search結果）
出力トークン/回	~500
入力コスト/回	~$0.035
出力コスト/回	~$0.0125
1銘柄あたり合計	~$0.33（約50円）
1セッション（10銘柄）
項目	見積もり
10銘柄合計	~$3.3（約500円）
月間コスト想定
週1回の実行 × 10銘柄 = 月4回
月間: ~$13（約2,000円）
---
10. ディレクトリ構成
```
swing-trading-curriculum/
├── docs/
│   └── research-tool-spec.md    ← 本ファイル（仕様書）
├── tools/
│   └── research/
│       ├── main.py              ← エントリーポイント
│       ├── tipsters/
│       │   ├── __init__.py
│       │   ├── base.py          ← 予想家の基底クラス
│       │   ├── tipster_a.py     ← トレンドテンプレート
│       │   ├── tipster_b.py     ← CAN SLIMファンダ
│       │   ├── tipster_c.py     ← イベントドリブン
│       │   ├── tipster_d.py     ← 出来高分析
│       │   ├── tipster_e.py     ← セクター分析
│       │   ├── tipster_f.py     ← 一目均衡表
│       │   └── tipster_g.py     ← 信用需給
│       ├── aggregator.py        ← 印ロジック（集計）
│       ├── reporter.py          ← レポート生成（Markdown/JSON）
│       ├── schemas.py           ← Structured Output スキーマ定義
│       └── config.py            ← 設定（モデル、閾値等）
├── output/                      ← 生成レポートの保存先
├── modules/                     ← 既存カリキュラム
├── HANDOFF.md
└── README.md
```
---
11. 設定ファイル
```python
# config.py

MODEL = "claude-opus-4-8"
MAX_TOKENS = 4096
MAX_STOCKS_PER_RUN = 10

MARK_THRESHOLDS = {
    "◎": 5,  # 7人中5人以上
    "○": 4,  # 7人中4人
    "▲": 3,  # 7人中3人
    "△": 0,  # 2人以下（デフォルト）
}

GOCHI_SETTINGS = {
    "min_trades_for_evaluation": 20,
    "elimination_win_rate_threshold": 0.40,
    "grace_period_trades": 10,
}
```
---
12. 実装フェーズ
Phase 1: 最小動作版（MVP）
スコープ: 予想家A（トレンドテンプレート）のみで1銘柄を評価
Claude API接続
web_search による情報収集
Structured Outputs による結果取得
基本的なCLI
Phase 2: 全予想家実装
スコープ: 予想家B〜Gの追加
各予想家のプロンプト実装
集計ロジック（印の決定）
Markdownレポート生成
Phase 3: 複数銘柄対応 + レポート
スコープ: 複数銘柄のバッチ処理とレポート
CSV入力対応
全銘柄のランキングレポート
JSON出力（ジャーナル連携用）
Phase 4: ゴチ方式連携
スコープ: トレードジャーナルとの連携
予想家成績の読み込み（ジャーナルから）
淘汰判定ロジック
退場/参戦の管理
---
13. 制約事項・リスク
リスク	対策
web_search の情報鮮度	最新データが取れない場合はレポートに「データ取得日」を明記
web_search のレート制限	銘柄間に適切なインターバルを設定
APIコスト超過	1回10銘柄の上限、月次コスト追跡
投資判断への過信	ツールはリサーチ補助。最終判断は人間（印はあくまで参考指標）
日本株データの英語偏り	web_search クエリを日本語で構成し、日本語ソースを優先
