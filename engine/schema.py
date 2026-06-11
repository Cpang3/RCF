# engine/schema.py
REQUIRED_FIELDS = (
    "ticker", "date", "decision", "conviction",
    "bull_thesis", "bear_thesis", "recent_run_pct",
    "catalyst_days", "reports", "raw_transcript",
)
VALID_DECISIONS = {"BUY", "SELL", "HOLD"}


def validate(decision: dict) -> dict:
    missing = [f for f in REQUIRED_FIELDS if f not in decision]
    if missing:
        raise ValueError(f"Decision missing fields: {missing}")
    if decision["decision"] not in VALID_DECISIONS:
        raise ValueError(f"Bad decision: {decision['decision']}")
    if not 0.0 <= decision["conviction"] <= 1.0:
        raise ValueError("conviction must be 0.0–1.0")
    return decision
