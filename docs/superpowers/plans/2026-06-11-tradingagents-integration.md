# TradingAgents Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the TauricResearch/TradingAgents multi-agent engine to RCF as a conviction analyzer that deep-analyzes screened finalists and emits a spot-position proposal, gated by RCF's rules.

**Architecture:** TradingAgents runs vanilla as a git submodule on the Mac. A thin RCF `engine/` adapter calls `TradingAgentsGraph.propagate(ticker, date)`; a pure-logic post-processor maps the buy/sell/hold output to RCF gates, ranks finalists, and proposes a sized **spot** position. Nothing auto-trades — proposals hand off to `tradingbot`/Futu with manual confirmation.

**Tech Stack:** Python 3.11+, LangGraph (via submodule), Anthropic Claude (tiered), pytest, PyYAML. **Runs on Mac only** (Windows `python.exe` is policy-blocked).

**Spec:** `docs/superpowers/specs/2026-06-11-tradingagents-integration-design.md`

---

## File Structure

| File | Responsibility |
|------|----------------|
| `tradingagents/` (submodule) | Vanilla TradingAgents engine. Not modified. |
| `engine/config.yaml` | Provider/model/cost config. Keys from env. |
| `engine/requirements.txt` | Adapter deps (pyyaml). |
| `engine/schema.py` | The normalized `Decision` dict contract + validation. |
| `engine/adapter.py` | Calls TradingAgentsGraph (mockable seam) → normalized Decision. |
| `engine/postprocess.py` | Pure logic: gate mapping, ranking, spot sizing, report rendering. |
| `engine/run_analysis.py` | Orchestrator: load finalists → adapter loop → postprocess → write `analysis/`. |
| `engine/tests/` | pytest unit + smoke tests (no API spend). |
| `risk_params.yaml` (modify) | Update for spot-only (per spec §7). |
| `analysis/` | Per-run outputs (md + json + transcript). |

**Normalized `Decision` dict contract (used across all tasks — keep field names identical):**
```python
{
  "ticker": str,            # "MU"
  "date": str,              # "2026-06-11"
  "decision": str,          # "BUY" | "SELL" | "HOLD"
  "conviction": float,      # 0.0–1.0, derived by adapter
  "bull_thesis": str,
  "bear_thesis": str,
  "recent_run_pct": float,  # trailing move attached upstream (for G5)
  "catalyst_days": int,     # days to catalyst, from rcf_universe.yaml (for T+52 gate)
  "reports": dict,          # raw section reports from TA
  "raw_transcript": str,
}
```

---

## Task 0: Submodule + engine scaffold

**Files:**
- Create: `engine/requirements.txt`, `engine/config.yaml`, `engine/__init__.py`, `engine/tests/__init__.py`
- Submodule: `tradingagents/`

- [ ] **Step 1: Add the TradingAgents submodule (pinned)**

```bash
git submodule add https://github.com/TauricResearch/TradingAgents.git tradingagents
cd tradingagents && git checkout main && git rev-parse HEAD && cd ..   # record this commit hash in the commit msg
```

- [ ] **Step 2: Create `engine/requirements.txt`**

```
pyyaml>=6.0
pytest>=8.0
```

- [ ] **Step 3: Create `engine/config.yaml`**

```yaml
provider: anthropic
deep_think_llm: claude-sonnet-4-6      # Trader + Researchers (confirm exact id at build)
quick_think_llm: claude-haiku-4-5-20251001  # 4 Analysts
max_debate_rounds: 1
online_tools: true
max_finalists_per_run: 3
# API keys are read from env: ANTHROPIC_API_KEY, ALPHAVANTAGE_API_KEY
```

- [ ] **Step 4: Create empty `engine/__init__.py` and `engine/tests/__init__.py`**

```bash
touch engine/__init__.py engine/tests/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add .gitmodules tradingagents engine
git commit -m "feat(engine): add TradingAgents submodule + engine scaffold"
```

---

## Task 1: Update risk_params.yaml for spot-only

**Files:**
- Modify: `risk_params.yaml` (the `risk_controls` block)
- Test: `engine/tests/test_risk_params.py`

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_risk_params.py
import yaml, pathlib

def _load():
    p = pathlib.Path(__file__).resolve().parents[2] / "risk_params.yaml"
    return yaml.safe_load(p.read_text())

def test_spot_only_no_contradiction():
    rc = _load()["risk_controls"]
    assert rc["defined_risk_required"] is False
    assert rc["instrument"] == "spot"
    assert rc["downside_via"] == ["position_sizing", "manual_stop_alert", "date_exit_T52"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest engine/tests/test_risk_params.py -v`
Expected: FAIL (KeyError / assertion — current file has `defined_risk_required: true`)

- [ ] **Step 3: Edit `risk_params.yaml` `risk_controls` block**

Replace the options-related keys with spot-only keys:
```yaml
risk_controls:
  noise_band_pct: 2.0
  soft_review_drawdown_pct: 5.0
  hard_stop_drawdown_pct: 10.0
  no_averaging_down: true
  reward_to_risk_min: 2.0
  # SPOT-ONLY (overrides prior defined-risk gate; see spec 2026-06-11 §7).
  # No native stop order exists; gap-through-stop risk accepted, mitigated by sizing.
  defined_risk_required: false
  instrument: spot
  downside_via: [position_sizing, manual_stop_alert, date_exit_T52]
```
Also set `gates.G2_defined_risk_structure_chosen` → rename to `G2_spot_sizing_set: false` and update `capital_allocation.max_single_name_pct: 100` (concentration into one name is intentional for RCF).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest engine/tests/test_risk_params.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add risk_params.yaml engine/tests/test_risk_params.py
git commit -m "fix(risk): switch risk_params to spot-only; resolve options contradiction"
```

---

## Task 2: Decision schema + adapter (mockable seam)

**Files:**
- Create: `engine/schema.py`, `engine/adapter.py`
- Test: `engine/tests/test_adapter.py`

- [ ] **Step 1: Write `engine/schema.py`**

```python
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
```

- [ ] **Step 2: Write the failing adapter test (with a fake graph)**

```python
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest engine/tests/test_adapter.py -v`
Expected: FAIL ("cannot import name normalize")

- [ ] **Step 4: Implement `engine/adapter.py`**

```python
# engine/adapter.py
import os, yaml, pathlib
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest engine/tests/test_adapter.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add engine/schema.py engine/adapter.py engine/tests/test_adapter.py
git commit -m "feat(engine): decision schema + adapter with mockable graph seam"
```

---

## Task 3: Post-processor — gates, ranking, spot sizing, report

**Files:**
- Create: `engine/postprocess.py`
- Test: `engine/tests/test_postprocess.py`

- [ ] **Step 1: Write failing tests for gate mapping + ranking + sizing**

```python
# engine/tests/test_postprocess.py
from engine.postprocess import map_gates, rank, propose_spot

BUY = {"ticker": "MU", "date": "2026-06-11", "decision": "BUY", "conviction": 0.8,
       "bull_thesis": "real catalyst thesis here", "bear_thesis": "b",
       "recent_run_pct": 4.0, "catalyst_days": 30, "reports": {}, "raw_transcript": ""}
HOLD = {**BUY, "ticker": "TSM", "decision": "HOLD", "conviction": 0.3}
RAN  = {**BUY, "ticker": "MRVL", "recent_run_pct": 32.0}   # already spiked

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest engine/tests/test_postprocess.py -v`
Expected: FAIL ("cannot import name map_gates")

- [ ] **Step 3: Implement `engine/postprocess.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest engine/tests/test_postprocess.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Add report rendering — failing test**

```python
# append to engine/tests/test_postprocess.py
from engine.postprocess import render_report

def test_render_report_contains_decision_and_proposal():
    rp = {"loan": {"principal_max_hkd": 705000},
          "capital_allocation": {"recommended_deployed_pct": 40},
          "risk_controls": {"hard_stop_drawdown_pct": 10}}
    p = propose_spot(BUY, rp, 120.0, 7.8)
    md = render_report(BUY, map_gates(BUY), p)
    assert "MU" in md and "BUY" in md and "282000" in md and "G5_not_chasing" in md
```

- [ ] **Step 6: Run to verify it fails, then implement `render_report`**

Run: `pytest engine/tests/test_postprocess.py::test_render_report_contains_decision_and_proposal -v` → FAIL

```python
# append to engine/postprocess.py
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
```

- [ ] **Step 7: Run all postprocess tests, then commit**

Run: `pytest engine/tests/test_postprocess.py -v` → all PASS
```bash
git add engine/postprocess.py engine/tests/test_postprocess.py
git commit -m "feat(engine): postprocess gates, ranking, spot sizing, report"
```

---

## Task 4: Orchestrator + smoke test (no API spend)

**Files:**
- Create: `engine/run_analysis.py`
- Test: `engine/tests/test_run_analysis.py`

- [ ] **Step 1: Write the failing smoke test (mocks the adapter)**

```python
# engine/tests/test_run_analysis.py
import json, pathlib
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
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest engine/tests/test_run_analysis.py -v`
Expected: FAIL ("module has no attribute run")

- [ ] **Step 3: Implement `engine/run_analysis.py`**

```python
# engine/run_analysis.py
import json, pathlib, argparse, yaml
from engine.adapter import analyze            # patched in tests
from engine import postprocess

def run(finalists: list, date: str, out_dir, risk_params: dict, usdhkd: float = 7.8):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    decisions = []
    for f in finalists:
        try:
            d = analyze(f["ticker"], date, f["recent_run_pct"], f["catalyst_days"])
        except Exception as e:                 # skip-and-log, never crash batch
            print(f"[skip] {f['ticker']}: {e}"); continue
        gates = postprocess.map_gates(d)
        proposal = postprocess.propose_spot(d, risk_params, f["price_usd"], usdhkd)
        (out / f"{d['ticker']}-{date}.md").write_text(
            postprocess.render_report(d, gates, proposal))
        (out / f"{d['ticker']}-{date}.json").write_text(
            json.dumps({"decision": d, "gates": gates, "proposal": proposal}, indent=2))
        decisions.append(d)
    ranked = postprocess.rank(decisions)
    print("Ranked BUYs:", [f"{d['ticker']}({d['conviction']})" for d in ranked])
    return ranked

def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--universe", default="rcf_universe.yaml")
    ap.add_argument("--risk", default="risk_params.yaml")
    ap.add_argument("--out", default="analysis")
    a = ap.parse_args()
    rp = yaml.safe_load(pathlib.Path(a.risk).read_text())
    uni = yaml.safe_load(pathlib.Path(a.universe).read_text())
    # finalists = entries with catalyst_days populated + price_usd (populated per-trade)
    finalists = [c for c in uni.get("finalists", [])]
    run(finalists, a.date, a.out, rp)

if __name__ == "__main__":
    _main()
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest engine/tests/test_run_analysis.py -v`
Expected: PASS

- [ ] **Step 5: Run the whole suite + commit**

Run: `pytest engine/ -v` → all PASS
```bash
git add engine/run_analysis.py engine/tests/test_run_analysis.py
git commit -m "feat(engine): orchestrator + smoke test (mocked adapter, no API spend)"
```

---

## Task 5: Live integration run (Mac, manual — costs real API $)

**Files:** none (verification only)

- [ ] **Step 1: Install + keys** (see spec §10): clone with `--recurse-submodules`, venv, `pip install -r tradingagents/requirements.txt -r engine/requirements.txt`, export `ANTHROPIC_API_KEY` + `ALPHAVANTAGE_API_KEY`.

- [ ] **Step 2: Populate one finalist** in `rcf_universe.yaml` under a `finalists:` list with real data:
```yaml
finalists:
  - {ticker: MU, recent_run_pct: 4.0, catalyst_days: 30, price_usd: 120.0}
```

- [ ] **Step 3: Run one live ticker (cheapest model first)**

Run: `python3 engine/run_analysis.py --date 2026-06-11`
Expected: `analysis/MU-2026-06-11.md` + `.json` written; console prints ranked BUYs. Confirm the decision + proposal read sensibly.

- [ ] **Step 4: Commit the run artifact (optional, for audit)**

```bash
git add analysis/ && git commit -m "chore(analysis): first live RCF engine run"
```

---

## Self-Review

- **Spec coverage:** D1 conviction-engine (Tasks 2–4) ✓; D2 submodule+adapter (Task 0, 2) ✓; D3 Claude tiered (config.yaml) ✓; D4 vanilla + postprocess (Tasks 2–3) ✓; D5 spot-only (Tasks 1, 3) ✓; D6 Mac/no-auto-trade (Task 5 manual handoff) ✓; gate mapping G5/G7 (Task 3) ✓; spec §7 risk_params update (Task 1) ✓; testing §8 (Tasks 2–4) ✓.
- **Placeholder scan:** model IDs flagged "confirm at build" (open item, not a silent gap); no TBD/TODO in code steps. ✓
- **Type consistency:** `Decision` dict fields identical across schema/adapter/postprocess/run_analysis; `propose_spot` returns dict-or-None consistently; `map_gates`/`rank`/`propose_spot`/`render_report` names stable. ✓

## Open items carried from spec §12
- Pin submodule commit hash (Task 0 Step 1).
- Confirm exact Claude model IDs (config.yaml).
- Populate real catalyst dates — still the binding G3 gate before any trade.
