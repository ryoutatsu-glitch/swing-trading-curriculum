TIPSTER_RESULT_SCHEMA = {
    "name": "tipster_evaluation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "証券コード",
            },
            "company_name": {
                "type": "string",
                "description": "企業名",
            },
            "tipster_id": {
                "type": "string",
                "description": "予想家ID（A〜G）",
            },
            "recommendation": {
                "type": "boolean",
                "description": "推奨するか否か",
            },
            "confidence": {
                "type": "integer",
                "description": "確信度（0-100）",
            },
            "criteria_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion": {
                            "type": "string",
                            "description": "評価項目名",
                        },
                        "passed": {
                            "type": "boolean",
                            "description": "基準を通過したか",
                        },
                        "detail": {
                            "type": "string",
                            "description": "判定根拠の詳細",
                        },
                    },
                    "required": ["criterion", "passed", "detail"],
                    "additionalProperties": False,
                },
                "description": "各評価項目の結果",
            },
            "summary": {
                "type": "string",
                "description": "評価の要約（1-2文）",
            },
            "data_sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "情報取得元のURL一覧",
            },
        },
        "required": [
            "ticker",
            "company_name",
            "tipster_id",
            "recommendation",
            "confidence",
            "criteria_results",
            "summary",
            "data_sources",
        ],
        "additionalProperties": False,
    },
}

STOCK_REPORT_SCHEMA = {
    "name": "stock_report",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "generated_at": {
                "type": "string",
                "description": "レポート生成日時（ISO 8601）",
            },
            "stocks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string"},
                        "company_name": {"type": "string"},
                        "mark": {
                            "type": "string",
                            "enum": ["◎", "○", "▲", "△"],
                            "description": "印",
                        },
                        "recommendation_count": {
                            "type": "integer",
                            "description": "推奨した予想家の数（0-7）",
                        },
                        "total_confidence": {
                            "type": "integer",
                            "description": "推奨した予想家の確信度合計",
                        },
                        "evaluations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tipster_id": {"type": "string"},
                                    "tipster_name": {"type": "string"},
                                    "recommendation": {"type": "boolean"},
                                    "confidence": {"type": "integer"},
                                    "summary": {"type": "string"},
                                },
                                "required": [
                                    "tipster_id",
                                    "tipster_name",
                                    "recommendation",
                                    "confidence",
                                    "summary",
                                ],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": [
                        "ticker",
                        "company_name",
                        "mark",
                        "recommendation_count",
                        "total_confidence",
                        "evaluations",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["generated_at", "stocks"],
        "additionalProperties": False,
    },
}
