# engine/postprocess.py
CHASING_RUN_PCT = 15.0   # > this trailing move = chasing (G5 fails)
MAX_CATALYST_DAYS = 52   # T+52 usable window


def map_gates(d: dict) -> dict:
    return {
        "G7_named_edge": bool(d.get("bull_thesis", "").strip()),
        "G5_not_chasing": d.get("recent_run_pct", 0.0) <= CHASING_RUN_PCT,
    }


def rank(decisions: list) -> list:
    buys = [d for d in decisions if d["decision"] == "BUY"]
    return sorted(buys, key=lambda d: d["conviction"], reverse=True)


def propose_spot(d: dict, risk_params: dict, price_usd: float, usdhkd: float):
    if d["decision"] != "BUY" or d["catalyst_days"] > MAX_CATALYST_DAYS:
        return None
    principal = risk_params["loan"]["principal_max_hkd"]
    deployed_pct = risk_params["capital_allocation"]["recommended_deployed_pct"]
    stop_pct = risk_params["risk_controls"]["hard_stop_drawdown_pct"]
    position_hkd = round(principal * deployed_pct / 100)
    shares = int(position_hkd / usdhkd / price_usd)
    return {
        "ticker": d["ticker"],
        "instrument": "spot",
        "position_hkd": position_hkd,
        "shares": shares,
        "entry": "tranche over T0–T+10 (3 buys)",
        "manual_stop_pct": stop_pct,
        "hard_stop_hkd": round(position_hkd * stop_pct / 100),
        "stop_mechanism": "Futu price-alert + manual exit (no native stop order)",
        "date_exit": "close by T+52",
        "catalyst_days": d["catalyst_days"],
    }


def render_report(d: dict, gates: dict, proposal) -> str:
    lines = [
        f"# {d['ticker']} — RCF analysis ({d['date']})",
        f"**Decision:** {d['decision']}  |  **Conviction:** {d['conviction']}",
        f"**Recent run:** {d['recent_run_pct']}%  |  **Catalyst in:** {d['catalyst_days']}d",
        "",
        "## Gates",
        *[f"- {k}: {v}" for k, v in gates.items()],
        "",
        "## Bull", d.get("bull_thesis", ""),
        "## Bear", d.get("bear_thesis", ""),
        "",
        "## Spot proposal",
        ("(none — not BUY or catalyst outside T+52)" if proposal is None
         else "\n".join(f"- {k}: {v}" for k, v in proposal.items())),
    ]
    return "\n".join(lines)
