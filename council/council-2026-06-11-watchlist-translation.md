# LLM Council — Watchlist → RCF Translation (2026-06-11)

**Question:** Battle-test translating the Trades 73-name, 3-tier diversified screening framework into the RCF leveraged 60-day strategy. Which criteria translate, which are dangerous, what's the right universe?

## Advisor summaries
- **Contrarian:** The screen optimizes for *survivable wrongness* (law of large numbers, tiny sizing, failure tolerance); RCF can't survive being wrong once. Tier 1C must not exist in RCF (documented failure mode on max leverage). Liquidity filters off by an order of magnitude. No catalyst-timing gate. "Don't translate it — rebuild from the constraint backward."
- **First Principles:** A watchlist answers a *portfolio* question; RCF asks a *single-conviction-bet* question. Sizing-as-diversification is meaningless when the position IS the portfolio. First-order for RCF: dated catalyst ≤ T+52, deep options liquidity (mega-cap only), IV/pricing that pays for borrow + tail, asymmetry. Reuse the 73 names only as a *liquidity universe*; rebuild selection from the catalyst outward.
- **Expansionist (constructive):** The vetted, thesis-tagged, catalyst-dated universe is a *deal-sourcing radar*. Two-speed machine: broad watchlist scans continuously; RCF fires on the single best in-window Tier-1A/1B setup. Tier system becomes a free leverage gate (1A/1B qualify, 1C is the incubator bench). Breadth feeds concentration.
- **Executor:** RCF gets its OWN static `rcf_universe.yaml` (don't filter master at runtime — inherits 1C exceptions). Raise mcap $5B→$20B, ADV 1M→3M, add options ADV ≥2000, hard `catalyst_date ≤ T+52`, exclude all 1C. New fields: catalyst_date (absolute), days_to_catalyst, catalyst_type, options_oi_atm, options_iv_rank, options_spread_pct, avg_gap_move_pct, liquidity_score. Naive runtime-filtering + equity-ADV-as-options-proxy + missing IV rank = the breakages.
- **Outsider:** Feeding your "everything I might trade" list — including the group you KNOW loses you money — into the highest-stakes borrowed-money decision makes no sense. Cross off all 28 of group 3 immediately; arguably group 2 too. Simple rule: borrowed money on a deadline only goes near a handful of giant liquid names. The list is a distraction from the real "don't-do-this" decision.

## Verdict
**Don't port wholesale — repurpose as a funnel.** Keep the filters (tightened ~4×), drop the tier-sizing logic (a diversification artifact), hard-exclude Tier 1C, add the binding `catalyst_date ≤ T+52` gate + options-liquidity + IV-rank fields. Build a static `rcf_universe.yaml` subset, not a runtime filter.

**Blind spot caught:** IV crush — defined-risk options *through* a high-IV earnings event can lose even when right on direction. RCF's "in-window catalyst" and "defined-risk options" preferences conflict at earnings; must be priced.

**Do first:** Add the hard `catalyst_date ≤ T+52` gate — it kills most of the list, which is correct.

→ Implemented in `UNIVERSE.md` + `rcf_universe.yaml`.
