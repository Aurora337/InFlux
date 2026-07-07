import json
import shutil
from pathlib import Path
import sys

sys.path.insert(0, ".")

from compare_env_reports import compare_reports


def test_compare_env_reports_pass():
    target = Path("data/replays/reports_test_pass")
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    reports = [
        {
            "environment": "Linux",
            "final_state_hash": "abc123",
            "replay_determinism_score": 1.0,
            "scenario_determinism_score": 1.0,
            "consensus_agreement_rate": 1.0,
            "ledger_integrity": "PASS",
        },
        {
            "environment": "Windows",
            "final_state_hash": "abc123",
            "replay_determinism_score": 1.0,
            "scenario_determinism_score": 1.0,
            "consensus_agreement_rate": 1.0,
            "ledger_integrity": "PASS",
        },
    ]

    paths = []
    for index, report in enumerate(reports, start=1):
        path = target / f"report_{index}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        paths.append(str(path))

    result = compare_reports(paths)

    assert result["cross_platform_determinism"] == "PASS"
    assert result["hash_match_all"]
    assert result["determinism_score_all_1"]
    assert result["ledger_integrity_all_pass"]

    shutil.rmtree(target)


def test_compare_env_reports_fail_on_hash_mismatch():
    target = Path("data/replays/reports_test_fail")
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    reports = [
        {
            "environment": "Linux",
            "final_state_hash": "abc123",
            "replay_determinism_score": 1.0,
            "scenario_determinism_score": 1.0,
            "consensus_agreement_rate": 1.0,
            "ledger_integrity": "PASS",
        },
        {
            "environment": "Docker",
            "final_state_hash": "zzz999",
            "replay_determinism_score": 1.0,
            "scenario_determinism_score": 1.0,
            "consensus_agreement_rate": 1.0,
            "ledger_integrity": "PASS",
        },
    ]

    paths = []
    for index, report in enumerate(reports, start=1):
        path = target / f"report_{index}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        paths.append(str(path))

    result = compare_reports(paths)

    assert result["cross_platform_determinism"] == "FAIL"
    assert not result["hash_match_all"]

    shutil.rmtree(target)
