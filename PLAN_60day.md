# PLAN — Capital Allocation in the 60-Day Window

**Status:** DESIGN. Not armed. Do not draw the loan until all gates in `risk_params.yaml` are green.
**Source spec:** `notes/yield_strategies_tradfi_sbs.md` (KFS-verified). **Battle-test:** `council/`.

---

## The core reframe (from the council)
- The **1% (HKD 7,050) is the cost; the risk is the drawdown** on deployed capital. Optimise the drawdown, not the fee.
- The **usable window is ~52 days, not 60** — FX both ways + T+1 settlement eat the last week. **Back-date everything to T+52.**
- **Defined-risk options are the unlock** — premium = max loss, immune to overnight gaps, no native stop-order needed.
- **Partial notional** (~30–40%) carries the same thesis at a fraction of cliff risk. Full 705k only if fully defined-risk.

---

## Two ways to express it (pick one BEFORE drawdown)

### Option A — Conservative / recommended
- Draw **partial** (e.g. HKD 300k) OR draw full but deploy ~40%.
- Express via **long calls or debit call spreads** expiring **inside T+52** on MU and/or MRVL.
- Max loss = total premium (sized ≤ HKD 77.6k). Cliff risk minimal; repayment never in doubt.

### Option B — Aggressive (only if every gate green + disciplined)
- Draw full 705k, deploy in 3 tranches into shares.
- **Mandatory** protective puts as the real stop (no mental stops on leveraged shares).
- Net premium cost raises break-even well above 1%; size accordingly.

> If neither A nor B has a catalyst that lands on/before T+52 → **no trade.** The financing is only worth it with a real in-window edge.

---

## Day-by-day (back-dated to T+52 close)

| Phase | Days | Action |
|-------|------|--------|
| **Pre-draw** | before T0 | All 8 gates green. Confirm MU/MRVL catalyst dates ≤ T+52. Mac + FX dry-run done. Written thesis + defined-risk structure chosen. |
| **Drawdown** | T0 | Draw loan (partial or full per chosen option). Convert HKD→USD **manually in-app**. |
| **Deploy** | T0–T+10 | Enter in 3 tranches (days 0, 4, 9). Never full-size into an intraday spike. Attach the defined-risk leg (option) at entry — the stop is not "set" until that leg exists. |
| **Hold** | T+10–T+45 | Monitor vs bands: 2% = noise, −5% = reassess, −10% = flatten. No averaging down. |
| **De-risk** | T+45–T+52 | Take partial profit if in target band. Begin closing. **Reconvert USD→HKD.** |
| **Hard close** | **T+52** | All positions flat, cash back in HKD. This is the real deadline. |
| **Repay** | T+52–T+60 | Principal in OCBC account before the interest-free window ends. Avoid the 3% + 48% cliff. |

---

## Allocation math (reference, full-notional case)
| Gross return | Gross P&L | − fee | Net P&L |
|---|---|---|---|
| +1% | 7,050 | 7,050 | 0 (break-even) |
| +5% | 35,250 | 7,050 | **+28,200** |
| +10% | 70,500 | 7,050 | **+63,450** |
| +20% | 141,000 | 7,050 | **+133,950** |
| −10% (hard stop) | −70,500 | 7,050 | **−77,550** |

On a **partial HKD 300k** deploy, scale all figures ×0.426 (max stop-loss ≈ HKD 33k) — same thesis, survivable cliff.

---

## Hard rules (the bot enforces these — see `risk_params.yaml`)
1. Status = ARMED only when all 8 gates pass.
2. No leveraged shares without a defined-risk (option) floor.
3. Catalyst must land on/before **T+52**.
4. Max one-name exposure ≤ 40% of deployed.
5. Hard close **T+52**; principal repaid by **T+60**.
6. Salary funds living only — never tops up or repays a losing trade.
7. No averaging down. No extending past 60 days.

---

## Open items before this can arm
- [ ] **G3 (critical):** confirm MU (~late Sept) and MRVL (~late Aug) earnings vs a T+52 close from your intended drawdown date — **they likely fall outside a window starting now.** If so: pick a different in-window catalyst, or delay drawdown to align, or stand down.
- [ ] G2: choose Option A vs B and the exact option structure/expiry.
- [ ] G6: complete Mac migration + small live order + FX dry-run both ways.
- [ ] G7: write the one-paragraph edge (what's mispriced, why, why now).
