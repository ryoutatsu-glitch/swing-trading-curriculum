import json
from abc import ABC, abstractmethod

import anthropic

from ..config import MAX_TOKENS, MODEL
from ..schemas import TIPSTER_RESULT_SCHEMA


class BaseTipster(ABC):
    tipster_id: str = ""
    tipster_name: str = ""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    @abstractmethod
    def build_prompt(self, ticker: str, company_name: str) -> str:
        ...

    def evaluate(self, ticker: str, company_name: str) -> dict:
        prompt = self.build_prompt(ticker, company_name)
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
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
            messages=[{"role": "user", "content": prompt}],
        )

        for block in response.content:
            if block.type == "text":
                return json.loads(block.text)

        return {
            "ticker": ticker,
            "company_name": company_name,
            "tipster_id": self.tipster_id,
            "recommendation": False,
            "confidence": 0,
            "criteria_results": [],
            "summary": "評価結果の取得に失敗しました",
            "data_sources": [],
        }
