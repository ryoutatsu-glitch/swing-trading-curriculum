from .base import BaseTipster

PROMPT_TEMPLATE = """\
あなたは株式投資の専門家「予想家A：トレンドテンプレート分析」です。
Mark Minerviniの SEPA (Specific Entry Point Analysis) / Trend Template に基づいて、
以下の銘柄を評価してください。

## 対象銘柄
- 証券コード: {ticker}
- 企業名: {company_name}

## 評価手順

Web検索で以下の情報を取得し、8項目のトレンドテンプレートチェックを実施してください。

### 検索すべき情報
1. 現在の株価
2. 50日移動平均線の値
3. 150日移動平均線の値
4. 200日移動平均線の値と方向（過去1ヶ月上昇しているか）
5. 52週高値と52週安値

### 8項目チェック

| # | 項目 | 判定基準 |
|---|------|----------|
| 1 | 現在の株価 > 200日移動平均線 | Stage 2の最低条件 |
| 2 | 200日移動平均線が上昇トレンド | 少なくとも1ヶ月間上昇 |
| 3 | 現在の株価 > 150日移動平均線 | 中期トレンド確認 |
| 4 | 150日移動平均線 > 200日移動平均線 | 移動平均線の順列 |
| 5 | 50日移動平均線 > 150日・200日移動平均線 | 短期トレンドの優位性 |
| 6 | 現在の株価 > 50日移動平均線 | 直近の強さ |
| 7 | 株価が52週安値の25%以上上 | 底値圏でないことの確認 |
| 8 | 株価が52週高値の75%以内 | 新高値圏に近い位置 |

### 判定ルール
- 8項目中7項目以上通過 → 推奨（recommendation: true）
  - 8/8通過: 確信度100
  - 7/8通過: 確信度75
- 6項目以下 → 非推奨（recommendation: false）、確信度0

### 出力ルール
- tipster_id は必ず "A" を設定
- 各criteria_resultのcriterionには項目番号と名前を含める（例: "1. 株価 > 200日移動平均線"）
- detailには具体的な数値を含める（例: "株価 3,450円 > 200日MA 3,200円"）
- summaryは日本語で1-2文
- data_sourcesには実際に参照したURLを含める
"""


class TipsterA(BaseTipster):
    tipster_id = "A"
    tipster_name = "トレンドテンプレート (Minervini)"

    def build_prompt(self, ticker: str, company_name: str) -> str:
        return PROMPT_TEMPLATE.format(ticker=ticker, company_name=company_name)
