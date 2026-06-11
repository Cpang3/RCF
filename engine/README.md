# engine/ — RCF conviction engine (runs on Mac)

Thin adapter over the [TradingAgents](https://github.com/TauricResearch/TradingAgents) submodule.
Deep-analyzes screened finalists → gates + ranking + **spot** position proposal. Never auto-trades.

> Windows note: `python.exe` is policy-blocked on the Windows machine. Run this on the Mac.

## Setup (Mac)
```bash
git clone --recurse-submodules https://github.com/Cpang3/RCF.git
cd RCF
# if TradingAgents submodule not yet added (first time only):
git submodule add https://github.com/TauricResearch/TradingAgents.git tradingagents

python3 -m venv .venv && source .venv/bin/activate
pip install -r engine/requirements.txt
pip install -r tradingagents/requirements.txt          # for live runs only

export ANTHROPIC_API_KEY=...        # live runs
export ALPHAVANTAGE_API_KEY=...     # live runs
```

## Verify the build (no API spend)
Run from the repo root so `engine` is importable:
```bash
pytest engine/ -v
```
Expected: all tests pass (`test_risk_params`, `test_adapter`, `test_postprocess`, `test_run_analysis`).

## Live run (costs API $)
1. Add a `finalists:` list to `rcf_universe.yaml` with real data, e.g.:
   ```yaml
   finalists:
     - {ticker: MU, recent_run_pct: 4.0, catalyst_days: 30, price_usd: 120.0}
   ```
2. `python3 engine/run_analysis.py --date 2026-06-11`
3. Read `analysis/<ticker>-<date>.md` + `.json`. Then execute the SPOT order via `tradingbot`/Futu (manual FX first; preview before confirm).

## Files
`config.yaml` (models/cost) · `schema.py` (Decision contract) · `adapter.py` (TA call + normalize) · `postprocess.py` (gates/rank/spot sizing/report) · `run_analysis.py` (orchestrator) · `tests/`.
