import json
import shutil
from pathlib import Path
import sys

sys.path.insert(0, "harness/replay-engine")

from replay_scenario_runner import run_all_scenarios


def test_replay_scenarios_aggregate_metrics():
    scenarios_dir = Path("tests/golden/_tmp_scenarios")
    output_root = Path("data/replays_test_batch")

    if scenarios_dir.exists():
        shutil.rmtree(scenarios_dir)
    if output_root.exists():
        shutil.rmtree(output_root)

    scenarios_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [
        {
            "name": "scenario_a",
            "epoch": 0,
            "supply": 1000.0,
            "participants": 100,
            "epochs": 4,
        },
        {
            "name": "scenario_b",
            "epoch": 0,
            "supply": 1200.0,
            "participants": 80,
            "epochs": 3,
        },
    ]

    for scenario in scenarios:
        path = scenarios_dir / f"{scenario['name']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scenario, f, indent=2)

    payload = run_all_scenarios(
        scenarios_dir=str(scenarios_dir),
        output_root=str(output_root),
    )

    assert payload["scenarios_checked"] == 2
    assert payload["scenarios_passed"] == 2
    assert payload["scenarios_failed"] == 0
    assert payload["blocks_checked"] == 7
    assert payload["blocks_failed"] == 0
    assert payload["replay_success_rate"] == 1.0
    assert payload["determinism_score"] == 1.0
    assert payload["ledger_integrity"] == "PASS"

    shutil.rmtree(scenarios_dir)
    shutil.rmtree(output_root)
