# engine/tests/test_run_analysis.py
import json
from engine import run_analysis


def fake_analyze(ticker, date, recent_run_pct, catalyst_days, **kw):
    return {"ticker": ticker, "date": date, "decision": "BUY", "conviction": 0.8,
            "bull_thesis": "t", "bear_thesis": "b", "recent_run_pct": recent_run_pct,
            "catalyst_days": catalyst_days, "reports": {}, "raw_transcript": ""}


def test_run_writes_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(run_analysis, "analyze", fake_analyze)
    finalists = [{"ticker": "MU", "recent_run_pct": 4.0, "catalyst_days": 30,
                  "price_usd": 120.0}]
    run_analysis.run(finalists, date="2026-06-11", out_dir=tmp_path,
                     risk_params={"loan": {"principal_max_hkd": 705000},
                                  "capital_allocation": {"recommended_deployed_pct": 40},
                                  "risk_controls": {"hard_stop_drawdown_pct": 10}})
    assert (tmp_path / "MU-2026-06-11.md").exists()
    rec = json.loads((tmp_path / "MU-2026-06-11.json").read_text())
    assert rec["decision"]["decision"] == "BUY" and rec["proposal"]["shares"] > 0
