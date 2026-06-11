# loan-convexity-strategy

**The "brain" for a leveraged, high-convexity, time-boxed AI-theme trade.**
Decision rules + thesis live here. Execution runs on the **`tradingbot`** repo (the "mechanism", Futu OpenAPI). Sibling layout:

```
claudecode/
├── tradingbot/                # MECHANISM — execution, broker, orders (github.com/Cpang3/tradingbot)
├── Trades/                    # general trading brain / rules (github.com/Cpang3/Trades)
└── loan-convexity-strategy/   # THIS — brain for the specific loan-funded AI-theme bet
```

This strategy does **not** re-implement execution. It defines *what / when / how-much / when-to-stop*, then hands a concrete order to `tradingbot` to place via Futu.

## Status: DESIGN — NOT FUNDED, NOT LIVE
LLM Council voted **5–0 against** the original framing (loan-funded all-in on SRAD). This repo exists to redesign the strategy so it could pass that bar — it has not yet.

## Eligible universe (AI-infrastructure theme)
- **MU** (Micron) — memory / HBM for AI
- **MRVL** (Marvell) — AI data-center connectivity, custom ASICs, optics
- Other AI-tier semis as added (NVDA, AVGO, AMD, …) — must genuinely fit the AI-infra thesis.

## Hard preconditions (gate, not guidelines)
See `STRATEGY.md`. Summary: verified loan terms, defined-risk stops, earnings-blackout, no single-name all-in, no chasing post-catalyst spikes, written/backtested edge.

## Artifacts
- `STRATEGY.md` — the rules
- `notes/` — source strategy notes (OCBC loan, cost model, risk framework)
- `council/` — the LLM Council verdict that shaped these rules
