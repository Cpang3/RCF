# 👋 RCF — Start Here (Mac Handoff)

Hey! This repo is the **RCF strategy**: a one-off, loan-funded, 60-day, **spot-only** convex trade on liquid AI-infra names, with a multi-agent analysis engine bolted on. Everything you need is here — this file is the map.

> **Why the handoff:** the Windows machine blocks `python.exe` (corporate AppLocker), so all execution lives on the **Mac**. Git/GitHub work fine; Python doesn't.

---

## 🚦 Current status: BUILT, not ARMED
The plumbing is done and pushed. The **trade is not live** — these gates are still `false` in `risk_params.yaml`:
- **G3_catalyst_inside_T52** ⚠️ *the big one* — MU (~late Sept) & MRVL (~late Aug) earnings likely fall **outside** a window starting now. No in-window catalyst = no edge.
- **G6_execution_proven** — Mac + FX dry-run not done.
- **G7_named_written_edge**, **G8_psychologically_ok**.

Don't draw the loan until all gates are green.

---

## 🗺️ What's in here
| File | What it is |
|------|-----------|
| `STRATEGY.md` | The rules + hard gates |
| `PLAN_60day.md` | Capital allocation, back-dated to a **T+52** close |
| `risk_params.yaml` | Machine-enforceable params (now **spot-only**) |
| `UNIVERSE.md` / `rcf_universe.yaml` | Screening criteria (Tier 1C banned, $20B/3M ADV floors, catalyst ≤ T+52) |
| `engine/` | The TradingAgents conviction engine (analysis → spot proposal) |
| `docs/superpowers/specs/` | The integration design spec |
| `docs/superpowers/plans/` | The TDD implementation plan |
| `council/` | The 3 LLM-Council battle-tests that shaped all of the above |

---

## ▶️ Next 3 steps on the Mac (≈10 min)
```bash
# 1. Clone + submodule
git clone --recurse-submodules https://github.com/Cpang3/RCF.git && cd RCF
git submodule add https://github.com/TauricResearch/TradingAgents.git tradingagents   # first time only

# 2. Env + verify the build (NO API cost)
python3 -m venv .venv && source .venv/bin/activate
pip install -r engine/requirements.txt
pytest engine/ -v          # ← should be all green

# 3. (Later, costs API $) live single-ticker run — see engine/README.md
```
**If `pytest` fails:** paste the output to Claude and it'll fix it. The code was authored on Windows and hand-traced but never run, so a green run here is the real confirmation.

---

## ⚖️ The one thing to keep honest
This is **borrowed money on a 60-day clock, spot-only (no options floor)**. The council's gap-risk warning is *accepted, not solved* — managed only by partial sizing + a manual price-alert stop + the hard T+52 exit. The cheap 1% fee is the *cost*; the real risk is the drawdown. Resolve **G3** (a real in-window catalyst) before anything else — without it, there's no trade worth funding.

*Friendly note: every decision here was pressure-tested by a 5-advisor council and is written down in `council/`. If a future you wonders "why spot-only?" or "why is Tier 1C banned?" — it's all in there.*
