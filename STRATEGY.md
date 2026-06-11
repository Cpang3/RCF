# STRATEGY — Loan-funded, time-boxed AI-theme convexity trade

**Last updated:** 2026-06-11
**Status:** DESIGN. Capital not deployed. Rules below are the bar the trade must clear.

---

## 1. Objective
Express a high-conviction AI-infrastructure view over a ~3-month window (Jul–Sep), with a defined-risk structure, optionally amplified by borrowed capital — WITHOUT the structural defects the LLM Council flagged.

## 2. Eligible universe
AI-infrastructure semis only. Vehicle MUST match the AI thesis (the SRAD mistake was a vehicle that didn't).
- **MU** — memory / HBM
- **MRVL** — data-center connectivity / custom silicon / optics
- Add others (NVDA, AVGO, AMD, TSM) only with a written one-line thesis each.

## 3. HARD GATES (all must be TRUE before any capital — borrowed or owned — is deployed)

| # | Gate | Why (Council finding) |
|---|------|----------------------|
| G1 | **OCBC Key Facts Statement verified in writing** — actual handling fee, whether interest accrues, and any covenant barring securities trading. | The "60-day interest-free" framing is likely a misread; the whole cost model rests on an unverified term. |
| G2 | **Defined-risk stop only.** Downside capped by a *protective put or debit spread*, never a price-alert "stop". | Toolset has no native stop-loss order; high-beta semis gap through price stops. |
| G3 | **Earnings blackout.** No full-size entry held naked through an earnings print inside the window. MU ≈ late Sept, MRVL ≈ late Aug — both land in-window. Through-earnings exposure must be option-defined. | Semis routinely gap 10–20% on earnings; a 10% stop is jumped. |
| G4 | **No single-name all-in.** Max one-name exposure capped (default ≤ 40% of trade capital); no 100% concentration. | The structural defect is concentration + leverage + fixed clock, independent of ticker. |
| G5 | **No chasing post-catalyst spikes.** Do not enter full size after a name has already run on a headline (e.g. MRVL +32% on the Jensen Huang "trillion-dollar" quote, 2026-06-02). | Buying hype after the move = negative expectancy. |
| G6 | **Repayment survives max loss.** Position sized so the *defined* max loss still leaves October repayment + ~HKD 30k headroom intact. | A 20% loss = ~2.8 months salary; repayment clock is fixed regardless of outcome. |
| G7 | **Named, written, ideally backtested edge.** A one-paragraph thesis stating what is mispriced and why, before risking a dollar. | "A conviction you can't name" is not a trade. |

> If any gate is FALSE → do not deploy. Borrowed capital requires ALL gates green.

## 4. Leverage policy
- Borrowed capital is permitted ONLY after G1–G7 are green AND only sized so max defined loss ≤ what owned savings could also have absorbed. Leverage amplifies a *defined* risk; it never converts an undefined risk into an acceptable one.
- Preferred sequencing: **prove the edge with owned capital / paper first**, then consider leverage.

## 5. Risk parameters (defaults — tune per trade)
- Noise tolerance: ~2% intraday = do nothing.
- Max defined loss per trade: set by option structure, target ≤ 10% of trade capital.
- No averaging down. A stopped/expired-worthless trade is closed, full stop (anti-revenge rule).

## 6. Execution handoff (→ tradingbot mechanism)
1. Strategy here produces: `{ticker, structure (shares/put/spread), size, entry condition, defined max-loss, exit}`.
2. FX (HKD→USD) done **manually in Futu/moomoo app** (no API conversion).
3. Order placed via `tradingbot` / futuapi `place_order.py` on **Mac** (Windows python is policy-blocked).
4. **Preview before `--confirmed`.** Confirm code/side/qty/price/session every time.
5. Log fill; attach the defined-risk leg (put/spread) immediately — the stop is not "set" until that leg exists.

## 7. Open items
- [ ] G1: obtain + read OCBC KFS
- [ ] Pick structure for MU and/or MRVL (shares + protective put vs debit spread)
- [ ] Confirm exact MU / MRVL earnings dates vs the holding window
- [ ] Decide owned-capital-first vs leverage, and the max one-name cap %
