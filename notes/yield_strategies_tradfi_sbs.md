# OCBC 60-Day Interest-Free Loan – Trading Strategy Framework

## 1. Product parameters (from KFS and offer)
- Loan type: unsecured personal instalment loan ("60-Day Interest-free Payment Holiday" Personal Loan).
- Loan amount (P): user plans HKD 705,000 (15× HKD 47,000 salary, within HKD 2,000,000 max).
- Tenor: 12 months (required for this variant).
- Handling fee: 1% per annum of approved loan amount, payable upfront on drawdown (either lump-sum or rolled into instalments).
- Interest during first 60 days: 0% (no interest charged for the first 60 days).
- Early settlement within 60-day holiday: no early repayment penalty if fully repaid within the 60-day interest-free holiday.
- Early settlement after 60 days: early repayment fee of 3% of original principal (min HKD 1,500) plus accrued interest and small residual interest to next due date.
- Overdue interest: default interest up to 48% p.a. on overdue amounts.
- Late fee: HKD 200 per missed instalment.

## 2. Core financial model (using P = HKD 705,000)

### 2.1 Deterministic loan costs
- Principal (P): 705,000.
- Handling fee (F): 1% × P = 0.01 × 705,000 = 7,050.
- Interest in first 60 days: 0.
- Early repayment fee inside 60 days: 0.

So if loan is drawn and fully repaid within the 60-day holiday, **total loan cost = HKD 7,050**, independent of trading result.

### 2.2 Trading P&L structure over the 60-day window
Let r be the gross return on the deployed capital over the 60-day period (as a fraction).

- Gross trading P&L = r × P.
- Net P&L after loan cost = r × P − F = r × 705,000 − 7,050.
- Break-even condition: r × 705,000 − 7,050 = 0 → r = 7,050 / 705,000 = 1.0%.

Therefore:
- Break-even 60-day portfolio return: ~1.0%.
- Every additional 1% of portfolio performance adds ~HKD 7,050 to net P&L.

### 2.3 Scenario table (for intuition)

| Gross return r | Gross P&L (r×P) | Loan fee F | Net P&L |
|----------------|-----------------|-----------|---------|
| +1%            | 7,050           | 7,050     | 0       |
| +2%            | 14,100          | 7,050     | 7,050   |
| +5%            | 35,250          | 7,050     | 28,200  |
| +10%           | 70,500          | 7,050     | 63,450  |
| +20%           | 141,000         | 7,050     | 133,950 |
| −5%            | −35,250         | 7,050     | −42,300 |
| −10%           | −70,500         | 7,050     | −77,550 |


## 3. Strategy design principles

### 3.1 High-level framing
- Treat this as a **one-off, time-boxed convex bet** with defined maximum duration (≤ 60 days) and maximum loss.
- The financing is efficient **only** if:
  - The full notional is repaid within the 60-day holiday.
  - No overdue instalments occur (no late fees or default interest).
- The salary cashflow is used purely as an operating buffer, not as additional risk capital.

### 3.2 Capital allocation
- Trading capital: HKD 705,000 (full loan amount).
- Do **not** haircut this amount for living expenses; instead, ringfence monthly salary for fixed costs and personal spending.
- Keep at least one month of total obligations (ZA loan, CRC, baseline living costs) as on-exchange or bank cash buffer, separate from the trading book.

### 3.3 Target return and stop-loss
Given the cost structure:
- Break-even: 1%.
- Attractive zone: ≥ 15–20% expected upside with realistic probability.
- Hard-loss cap: around 10% drawdown on full position.

Proposed rules:
- Normal noise band: tolerate up to 2% adverse move without action.
- Soft review: at 5% drawdown, reassess thesis, newsflow, and liquidity.
- Hard stop: at 10% drawdown (≈ HKD 77.6k net loss including fee), flatten the position and repay the loan from available cash.

This forces a payoff profile where:
- Upside: in realistic best case 15–30% upside on P.
- Downside: capped at ~11–12% of P in total (10% trading loss + 1% fee).

## 4. Timeline and cashflow plan

### 4.1 Suggested timeline
- T0 (drawdown): draw the loan once the trading setup is identified and ready.
- T0 to T+10 days: deploy into the chosen trade(s) in 1–3 tranches; avoid immediate full-sizing into unstable intraday spikes.
- T+10 to T+45 days: main holding window; monitor P&L versus stop and target bands.
- T+45 to T+55 days: begin de-risking, partial profit-taking if target band reached; avoid carrying maximum exposure into the final 5–10 days.
- By T+55: aim to have closed the position and converted back to HKD.
- T+55 to T+60: hold cash, repay full outstanding principal before the interest-free window ends.

### 4.2 Monthly cashflow and obligations
- Salary at time of trade: HKD 47,000 rising to HKD 55,000 later in the year (check actual timing before drawdown).
- Fixed obligations: HKD 7,000 (ZA loan) + HKD 3,000 (CRC/other) ≈ HKD 10,000 per month.
- No rent: large advantage; use this to maintain comfortable cash reserves.

Operating rules:
- Keep **at least HKD 30,000** in non-trading cash at all times for living costs and emergencies.
- Never use trading P&L to increase lifestyle spending until after loan has been fully repaid and capital returned to neutral.


## 5. Market and instrument selection

### 5.1 Target characteristics
Given the 60-day horizon and convex payoff target, ideal trades should have:
- Realistic 15–30% upside potential over a 1–2 month window.
- High liquidity, tight spreads, and deep order books to support entry/exit in HKD 700k size without excessive slippage.
- Clear catalysts within the 60-day window: earnings, product launches, regulatory events, or macro data around themes you know (e.g., AI / infra / stablecoin eco-system plays).
- Availability on venues where you already trade efficiently (Binance, major CEXs) or liquid equities with margin support.

### 5.2 Example categories
- Liquid AI infrastructure equities or ETFs with defined catalyst dates.
- High-liquidity crypto majors or large-cap ecosystem tokens tied to near-term events.
- Structured trades (e.g., options spreads) if you want to define payoff more tightly, but only if margin, liquidation, and greeks are fully understood.


## 6. Risk controls and failure modes

### 6.1 Key risks
- Market gap risk: overnight or weekend moves beyond the 10% stop.
- Execution risk: inability to exit size quickly without moving the market.
- Behavioural risk: failing to execute the stop because of anchoring or FOMO.
- Operational risk: forgetting the loan dates, missing a repayment, or misreading the terms.

### 6.2 Mitigations
- Use hard stop orders or conditional orders where venue is reliable; otherwise, manual stop with explicit rule that overrides discretionary views.
- Size in 2–3 tranches instead of a single block; be willing to cut faster if liquidity thins or spreads widen.
- Maintain a written trading plan (entries, target, stop, and date-based exit) before entering the position; no averaging-down beyond the planned sizing.
- Set calendar reminders for:
  - Loan drawdown date.
  - 45-day, 55-day, and 60-day checkpoints.


## 7. Decision criteria and go/no-go checklist

Before drawing the loan, check:
1. Loan documentation:
   - Written confirmation of 1% fee.
   - Written confirmation that **full repayment within 60 days = no early settlement penalty**.
2. Personal balance sheet:
   - No new large obligations expected in the 60-day window.
   - Comfortable cash buffer (≥ HKD 30,000) set aside.
3. Trade quality:
   - Clear thesis with time-bound catalyst inside 60 days.
   - Defined target and stop levels with acceptable payoff ratio (>2:1 reward:risk).
   - Venue and instrument vetted for liquidity and counterparty risk.
4. Psychological readiness:
   - You are willing to accept a ~HKD 80k max loss scenario without life-impacting stress.

If any of these fail, **do not draw the loan**.


## 8. Summary rule-set (for later execution)

- Borrow: HKD 705,000 via OCBC 60-Day Interest-free Personal Loan (12-month tenor, 1% fee).
- Cost: accept fixed cost of HKD 7,050 as the ticket price for the trade.
- Horizon: close all positions and repay loan **within 55–60 days** of drawdown.
- Target: seek trades with realistic 15–30% upside, but be satisfied with locking 5–10% if achieved early.
- Stop-loss: cut the position at around 10% drawdown on total capital, no exceptions.
- Liquidity: only use instruments where HKD 700k can enter and exit cleanly.
- Cash discipline: ringfence salary for living and obligations; maintain HKD 30k+ buffer.
- Behaviour: no averaging-down beyond pre-planned sizing, no extending the trade beyond 60 days.

Use this document as a checklist and parameter sheet when you are closer to execution; revise figures if your salary, obligations, or OCBC’s exact offer terms change.
