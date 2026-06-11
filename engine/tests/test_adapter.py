# engine/tests/test_adapter.py
from engine.adapter import normalize


def test_normalize_maps_raw_to_contract():
    raw = {
        "final_trade_decision": "BUY",
        "investment_debate_state": {"bull_history": "bull...", "bear_history": "bear..."},
        "trader_investment_plan": "plan...",
    }
    d = normalize(raw, ticker="MU", date="2026-06-11",
                  recent_run_pct=4.0, catalyst_days=30)
    assert d["ticker"] == "MU"
    assert d["decision"] == "BUY"
    assert d["bull_thesis"] == "bull..."
    assert 0.0 <= d["conviction"] <= 1.0
