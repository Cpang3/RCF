# engine/tests/test_risk_params.py
import yaml
import pathlib


def _load():
    p = pathlib.Path(__file__).resolve().parents[2] / "risk_params.yaml"
    return yaml.safe_load(p.read_text())


def test_spot_only_no_contradiction():
    rc = _load()["risk_controls"]
    assert rc["defined_risk_required"] is False
    assert rc["instrument"] == "spot"
    assert rc["downside_via"] == ["position_sizing", "manual_stop_alert", "date_exit_T52"]
