# engine/adapter.py
import yaml
import pathlib
from engine.schema import validate


def _conviction(decision: str, raw: dict) -> float:
    # Derived: BUY/SELL carry directional conviction, HOLD is low.
    base = {"BUY": 0.7, "SELL": 0.7, "HOLD": 0.3}.get(decision, 0.3)
    # nudge by debate length asymmetry if present
    st = raw.get("investment_debate_state", {})
    bull, bear = len(st.get("bull_history", "")), len(st.get("bear_history", ""))
    if bull + bear:
        skew = (bull - bear) / (bull + bear)        # -1..1
        base = min(1.0, max(0.0, base + 0.15 * skew if decision == "BUY" else base))
    return round(base, 3)


def normalize(raw: dict, ticker: str, date: str,
              recent_run_pct: float, catalyst_days: int) -> dict:
    decision = str(raw.get("final_trade_decision", "HOLD")).upper().strip()
    if decision not in {"BUY", "SELL", "HOLD"}:
        decision = "HOLD"
    st = raw.get("investment_debate_state", {})
    return validate({
        "ticker": ticker, "date": date, "decision": decision,
        "conviction": _conviction(decision, raw),
        "bull_thesis": st.get("bull_history", ""),
        "bear_thesis": st.get("bear_history", ""),
        "recent_run_pct": recent_run_pct,
        "catalyst_days": catalyst_days,
        "reports": raw, "raw_transcript": str(raw),
    })


def analyze(ticker: str, date: str, recent_run_pct: float, catalyst_days: int,
            graph=None, config_path=None) -> dict:
    """Live call. `graph` injectable for tests so no API is hit."""
    if graph is None:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        cfg = yaml.safe_load(pathlib.Path(
            config_path or "engine/config.yaml").read_text())
        graph = TradingAgentsGraph(config=cfg)   # keys via env
    _state, raw = graph.propagate(ticker, date)
    return normalize(raw, ticker, date, recent_run_pct, catalyst_days)
