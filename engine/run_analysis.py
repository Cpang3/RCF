# engine/run_analysis.py
import json
import pathlib
import argparse
import yaml
from engine.adapter import analyze            # patched in tests
from engine import postprocess


def run(finalists: list, date: str, out_dir, risk_params: dict, usdhkd: float = 7.8):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    decisions = []
    for f in finalists:
        try:
            d = analyze(f["ticker"], date, f["recent_run_pct"], f["catalyst_days"])
        except Exception as e:                 # skip-and-log, never crash batch
            print(f"[skip] {f['ticker']}: {e}")
            continue
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
