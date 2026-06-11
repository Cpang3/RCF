# Spec — TradingAgents Integration for RCF (spot-only, Mac)

**Date:** 2026-06-11
**Status:** DESIGN APPROVED — ready for implementation plan
**Repo:** RCF (`github.com/Cpang3/RCF`)
**Runs on:** Mac only (Windows `python.exe` is blocked by corporate policy).

---

## 1. Purpose
Add a multi-agent analysis engine ([TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)) to RCF as the **conviction engine** that deep-analyzes the handful of finalists surfaced by RCF's mechanical screen (`rcf_universe.yaml`). Its output feeds RCF's gates and selection. It does **not** screen, decide position structure, or execute — RCF and `tradingbot` own those.

## 2. Locked decisions
| # | Decision | Choice |
|---|----------|--------|
| D1 | Role of TradingAgents | **Deep-analysis engine on finalists** (downstream of the mechanical screen, upstream of RCF gates) |
| D2 | Repo integration | **Git submodule + thin adapter in RCF** (`engine/`) |
| D3 | LLM provider/cost | **Claude, tiered** — deep=Opus/Sonnet (Trader + Researchers), quick=Haiku (4 Analysts), `max_debate_rounds`=1–2 |
| D4 | Coupling | **Vanilla engine + RCF post-processor** (TA unmodified; RCF translates output) |
| D5 | Instrument | **Spot (shares) only — no options** |
| D6 | Platform | **Mac only**; never auto-trades (emits proposals; `tradingbot` executes with preview-before-confirm) |

## 3. Architecture & data flow
```
rcf_universe.yaml ──(gates: tier∈{1A,1B}, ≥$20B mcap, ≥3M ADV, catalyst_date ≤ T+52)──► finalists
        │
        ▼
engine/run_analysis.py ──(ticker, date)──► tradingagents/ submodule (VANILLA)
        ▲                                    TradingAgentsGraph(config).propagate()
        │  decision (buy/sell/hold) + analyst/researcher/trader/risk/PM reports │
        └─────────────────────────────────────────────────────────────────────┘
        ▼
engine/postprocess.py (the RCF brain):
   • parse decision + extract bull/bear thesis      → gate G7 (named written edge)
   • detect recent run / catalyst already passed     → gate G5 (not chasing a spike)
   • rank finalists by conviction                    → select single best (concentration ≤40%)
   • IF BUY & catalyst_date ≤ T+52 → PROPOSE a SPOT position:
        - share qty sized per risk_params.yaml (partial notional, ≤40% one name)
        - entry plan (tranches), manual stop level + price-alert, hard date exit (T+52)
        ▼
   writes: analysis/<ticker>-<YYYY-MM-DD>.md (human report) + analysis/<ticker>-<date>.json (decision record)
        ▼
   handoff → tradingbot (Futu, Mac): preview before confirm. Never auto-trades.
```

## 4. Components (new in RCF)
- **`tradingagents/`** — git submodule pinned to a specific commit. The vanilla engine. Not modified.
- **`engine/config.yaml`** — provider=anthropic; `deep_think_llm`, `quick_think_llm`, `max_debate_rounds`, cost caps, `max_finalists_per_run`. **All API keys read from env, never committed.**
- **`engine/adapter.py`** — builds the TradingAgents config from `engine/config.yaml`, calls `TradingAgentsGraph(...).propagate(ticker, date)`, returns a normalized `dict` (`decision`, `conviction`, `bull_thesis`, `bear_thesis`, `reports`, `raw_transcript`). **`conviction` is derived by the adapter** (TA returns buy/sell/hold, not a score) — e.g. from the decision + the bull/bear debate balance + Portfolio-Manager approval; exact formula defined in the implementation plan.
- **`engine/run_analysis.py`** — orchestrator. Loads in-window finalists from `rcf_universe.yaml`, loops the adapter (skip-and-log on per-ticker failure), persists raw decisions to `analysis/`.
- **`engine/postprocess.py`** — pure RCF logic (no LLM calls): decision → gate mapping, conviction ranking, **spot** position proposal, report + JSON writing.
- **`analysis/`** — per-run audit trail (human `.md` + machine `.json` + raw transcript). Mirrors the council artifact pattern.
- **`engine/tests/`** — see §8.

## 5. Conviction → gate mapping (postprocess)
- TA **BUY** → eligible candidate; bull/bear thesis text populates **G7** (named written edge). Conviction score ranks finalists.
- TA **HOLD/SELL** → dropped from RCF candidates.
- **G5 (not chasing):** adapter computes recent % run and whether the catalyst already fired; flags if entering after the move (e.g. the MRVL +32% Jensen-Huang spike precedent).
- RCF picks the **single best** finalist (concentration); it does not build a basket.

## 6. Spot position proposal (replaces the prior options-structuring step)
Given BUY + `catalyst_date ≤ T+52`, postprocess emits a **proposal** (not an order):
- **Share quantity** sized to `risk_params.yaml`: partial notional (default ~40% deployed), one-name cap ≤40%, max defined loss kept ≤ the hard-stop budget.
- **Entry:** 1–3 tranches over the first ~10 days.
- **Downside (no options floor):** a **manual stop level** + a **Futu price-alert** (the toolset supports price reminders), plus the **hard date exit at T+52**. No native stop order exists.
- **Exit:** target band + mandatory close by T+52 (then reconvert USD→HKD, repay by T+60).

## 7. ⚠️ Risk note — spot-only deviation from the council
The 2026-06-11 debt battle-test concluded the trade is only sound if expressed as **defined-risk options** (premium = max loss) because the toolset has **no native stop-loss** and AI-infra names **gap through price stops** on catalysts. **Spot-only (D5) removes that floor.** Consequences carried into the design:
- The gap-through-stop risk the council flagged is now **accepted**, not eliminated.
- Mitigation reverts to: **smaller / partial notional**, **manual stop + price-alert discipline**, and the **hard T+52 date exit**.
- This **reverses** `risk_params.yaml` gate **G2 (`defined_risk_required`)** and `preferred_instrument: long_options_or_debit_spreads` / `shares_with_mental_stop: DISALLOWED`. **Implementation must update `risk_params.yaml`** to reflect spot-only with sizing-based risk control, and record the override explicitly (don't leave the file self-contradicting).
- `rcf_universe.yaml` options-liquidity gates (`options_oi_atm`, `options_iv_rank`, `options_spread_pct`) become **N/A**; equity liquidity gates (≥$20B mcap, ≥3M ADV) remain binding for moving ~HKD 700k of spot.

## 8. Testing
- **Unit (no API spend):** `postprocess.py` against fixture decision-JSON — mapping, ranking, spot-sizing, gate flags. This is the load-bearing logic.
- **Smoke:** mock `TradingAgentsGraph.propagate()` so `run_analysis.py` runs end-to-end without LLM calls.
- **Live integration (Mac):** one ticker, cheapest model, confirm keys + data wiring.

## 9. Cost & error handling
- Bounded by `max_finalists_per_run` + low `max_debate_rounds` + Haiku analysts. Log estimated $ per run.
- Per-ticker failure (missing data) → skip + log, never crash the batch.
- LLM non-determinism → persist full transcript per run for audit.
- Secrets from env only; `.gitignore` already excludes `.env`, tokens, account artifacts.

## 10. Mac handoff — setup & run
> Designed so you can clone RCF on the Mac and go. (Python runs on Mac; it does not on the Windows box.)

```bash
# 1. Clone RCF with submodules
git clone --recurse-submodules https://github.com/Cpang3/RCF.git
cd RCF
# (if already cloned) git submodule update --init --recursive

# 2. Python env + deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r tradingagents/requirements.txt
pip install -r engine/requirements.txt        # adapter deps (pyyaml etc.)

# 3. API keys (env — never commit)
export ANTHROPIC_API_KEY=...
export ALPHAVANTAGE_API_KEY=...

# 4. Configure models/costs
$EDITOR engine/config.yaml

# 5. Run the engine over in-window finalists
python3 engine/run_analysis.py --date 2026-06-11
#   → writes analysis/<ticker>-<date>.md + .json

# 6. Review the proposal, then execute the SPOT order via tradingbot/Futu
#    (manual FX HKD→USD first; preview before --confirmed)
```

## 11. Out of scope / boundaries
- TradingAgents internals are **not** modified.
- No options, no auto-trading, no basket.
- Execution (order placement, FX) stays in `tradingbot` / futuapi with manual confirmation.
- This spec covers the analysis→proposal pipeline only; the `tradingbot` enforcement loader for `risk_params.yaml` is a separate piece.

## 12. Open items (resolve during/after implementation)
- [ ] Update `risk_params.yaml` for spot-only (per §7) — required, or the repo self-contradicts.
- [ ] Pin the TradingAgents submodule commit.
- [ ] Confirm exact Claude model IDs for deep/quick at build time.
- [ ] Populate `rcf_universe.yaml` finalists with real catalyst dates (still the binding G3 gate).
