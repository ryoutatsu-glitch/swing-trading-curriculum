MODEL = "claude-opus-4-8"
MAX_TOKENS = 4096
MAX_STOCKS_PER_RUN = 10

MARK_THRESHOLDS = {
    "◎": 5,
    "○": 4,
    "▲": 3,
    "△": 0,
}

GOCHI_SETTINGS = {
    "min_trades_for_evaluation": 20,
    "elimination_win_rate_threshold": 0.40,
    "grace_period_trades": 10,
}
