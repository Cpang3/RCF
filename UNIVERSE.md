# UNIVERSE — Screening criteria for RCF (translated from the Trades watchlist)

**Source:** `Trades/watchlist.MD` (73-name, 3-tier diversified position-trading universe).
**Battle-test:** `council/council-2026-06-11-watchlist-translation.md`.
**Status:** framework defined; per-name data (catalyst dates, options metrics) populated per-trade — **not fabricated here.**

---

## The core principle (why this is NOT a copy of the watchlist)
The Trades watchlist optimizes for **survivable wrongness** across a diversified book — many small positions, tiered sizing as a diversification mechanism, tolerance for failure (3 strikes before suspension). **RCF is the opposite:** one-off, borrowed, concentrated, 60-day clock. Under leverage + concentration, the tier-sizing logic **dissolves** — the position *is* the portfolio. So we keep the *filters*, tighten them ~4×, drop the *sizing tiers*, and add the constraints the old screen never had.

## The two-speed model
- **Watchlist (the radar):** the full 73-name Trades universe keeps scanning continuously — cheap, broad, thesis-tagged, catalyst-dated.
- **RCF (the trigger):** fires only on the single best **in-window, Tier-1A/1B, deep-options-liquidity** setup the radar surfaces. Breadth feeds concentration.

## What translates, what changes, what's banned

| Trades criterion | RCF treatment |
|---|---|
| Tier 1A (mega-cap, 1.0% sizing) | **Eligible.** Sizing tiers dropped (irrelevant under concentration). |
| Tier 1B (≥$5B narrative, 0.5%) | **Eligible ONLY if** it clears the raised floors below **AND** has a dated catalyst ≤ T+52. |
| Tier 1C (sub-$5B narrative, 0.25%) | **HARD EXCLUDED. No override.** This is the user's documented failure mode — never on borrowed money. |
| mcap ≥ $5B | **Raised to ≥ $20B** (700k slug + tight options spreads). |
| ADV ≥ 1M shares | **Raised to ≥ 3M shares.** |
| options OI > 1000, bid-ask < 5% | **Kept, and made first-order** — options liquidity is the real gate, not equity ADV. Add options ADV ≥ 2000 contracts/day. |
| earnings_date (optional field) | **Now mandatory & binding:** `catalyst_date ≤ T+52`. No dated in-window catalyst → not eligible. |
| tier-based sizing 0.25/0.5/1.0% | **Removed.** Replaced by RCF's concentration cap (≤40% one name) + defined-risk premium sizing in `risk_params.yaml`. |
| failure_mode_check / override discipline | **Moot** — 1C is excluded, so overrides don't exist in RCF. |

## New gates RCF adds (absent from the watchlist)
1. **`catalyst_date ≤ T+52`** — absolute date, not relative. *Binding.*
2. **IV-rank awareness** — buying defined-risk options *through* a high-IV-rank earnings event risks vol crush even when right on direction. Flag `options_iv_rank`; prefer pre-catalyst entry or spreads that fund the crush.
3. **`avg_gap_move_pct`** — historical event-day gap sizes the option-spread width and confirms the −10% share stop is unusable.
4. **Defined-risk only** (from `risk_params.yaml`) — names need liquid option chains to express the trade as bounded-loss structures.

## Candidate pool (from the watchlist, by liquidity — NOT a buy list)
Tier 1A: **NVDA, AMD, GOOGL, META, TSLA** (+ AAPL, MSFT, AMZN, SPY, QQQ auto-pass).
Tier 1B that *may* qualify on the ≥$20B / deep-options floor (each still needs a dated ≤T+52 catalyst + options check): TSM, MU, MRVL, ARM, QCOM, ORCL, NOW, APP, SHOP, IBM, PLTR, LMT, COIN, HOOD, NU, RKT, FSLR, DELL, HPE, RKLB, ASTS, SATS.
**Everything Tier 1C is excluded.** Borderline-mcap 1C names (ZETA, RDW, AMTM, LUNR) do **not** get promoted for RCF.

> Final eligibility is decided per-trade by `rcf_universe.yaml` once catalyst + options fields are populated with real data. This file is the rulebook, not the trade.
