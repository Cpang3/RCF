# engine/tests/test_postprocess.py
from engine.postprocess import map_gates, rank, propose_spot, render_report

BUY = {"ticker": "MU", "date": "2026-06-11", "decision": "BUY", "conviction": 0.8,
       "bull_thesis": "real catalyst thesis here", "bear_thesis": "b",
       "recent_run_pct": 4.0, "catalyst_days": 30, "reports": {}, "raw_transcript": ""}
HOLD = {**BUY, "ticker": "TSM", "decision": "HOLD", "conviction": 0.3}
RAN = {**BUY, "ticker": "MRVL", "recent_run_pct": 32.0}   # already spiked


def test_gates_buy_passes_g7_and_g5():
    g = map_gates(BUY)
    assert g["G7_named_edge"] is True          # has a thesis
    assert g["G5_not_chasing"] is True         # 4% run < threshold


def test_gates_flags_chasing_on_big_run():
    assert map_gates(RAN)["G5_not_chasing"] is False   # 32% run


def test_rank_keeps_only_buys_sorted_by_conviction():
    out = rank([HOLD, BUY])
    assert [d["ticker"] for d in out] == ["MU"]


def test_propose_spot_sizes_position():
    rp = {"loan": {"principal_max_hkd": 705000},
          "capital_allocation": {"recommended_deployed_pct": 40},
          "risk_controls": {"hard_stop_drawdown_pct": 10}}
    p = propose_spot(BUY, rp, price_usd=120.0, usdhkd=7.8)
    assert p["position_hkd"] == 282000
    assert p["shares"] == int(282000 / 7.8 / 120.0)
    assert p["hard_stop_hkd"] == 28200


def test_propose_spot_none_when_catalyst_out_of_window():
    rp = {"loan": {"principal_max_hkd": 705000},
          "capital_allocation": {"recommended_deployed_pct": 40},
          "risk_controls": {"hard_stop_drawdown_pct": 10}}
    assert propose_spot({**BUY, "catalyst_days": 60}, rp, 120.0, 7.8) is None


def test_render_report_contains_decision_and_proposal():
    rp = {"loan": {"principal_max_hkd": 705000},
          "capital_allocation": {"recommended_deployed_pct": 40},
          "risk_controls": {"hard_stop_drawdown_pct": 10}}
    p = propose_spot(BUY, rp, 120.0, 7.8)
    md = render_report(BUY, map_gates(BUY), p)
    assert "MU" in md and "BUY" in md and "282000" in md and "G5_not_chasing" in md
