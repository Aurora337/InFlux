import json
import shutil
from pathlib import Path
import sys

sys.path.insert(0, "harness/economic-stress")

from economic_verification_engine import load_economic_scenario, run_economic_scenario, run_economic_suite


def _copy_scenarios(tmp_dir: Path) -> Path:
    target = tmp_dir / "scenarios"
    target.mkdir(parents=True, exist_ok=True)
    for scenario_file in Path("scenarios/economic").glob("*.json"):
        shutil.copy2(scenario_file, target / scenario_file.name)
    return target


def test_economic_verification_long_horizon():
    tmp_dir = Path("data/economic_verification_test")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    scenarios_dir = _copy_scenarios(tmp_dir)
    long_horizon = load_economic_scenario(scenarios_dir / "long_horizon_growth.json")
    report_dir = tmp_dir / "reports"
    report = run_economic_scenario(long_horizon, report_dir=report_dir)

    assert report.blocks_simulated == 100000
    assert report.ledger_integrity == "PASS"
    assert report.ending_supply > report.beginning_supply
    assert report.ending_supply < long_horizon.target_supply_cap * 2
    assert report.ending_reserve >= 0
    assert report.average_delta_c >= 0
    assert report.max_delta_c >= report.average_delta_c
    assert report.final_state_hash

    shutil.rmtree(tmp_dir)


def test_economic_verification_suite():
    tmp_dir = Path("data/economic_verification_suite_test")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    scenarios_dir = _copy_scenarios(tmp_dir)
    report_dir = tmp_dir / "reports"
    payload = run_economic_suite(scenarios_dir=scenarios_dir, report_dir=report_dir)

    assert payload["scenarios_checked"] == 10
    assert payload["scenarios_passed"] == 10
    assert payload["scenarios_failed"] == 0
    assert payload["blocks_simulated"] >= 100000 + 365 * 7 + 1825 + 3650
    assert payload["ledger_integrity"] == "PASS"
    assert payload["max_delta_c"] >= payload["average_delta_c"]
    assert payload["reproduction_events"] > 0
    assert payload["reserve_utilization"] >= 0

    metrics_path = report_dir / "metrics.json"
    assert metrics_path.exists()
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    assert metrics["ledger_integrity"] == "PASS"

    shutil.rmtree(tmp_dir)
