"""Scenario-driven replay audit runner with aggregate determinism metrics."""

from dataclasses import dataclass
from pathlib import Path
import json
import shutil
import sys

sys.path.insert(0, "src")

from influx.kernel.state import State
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash
from influx.kernel.ledger.block_store import BlockStore
from replay_audit import audit_ledger_replay


@dataclass
class ScenarioRunResult:
    scenario_name: str
    data_dir: str
    blocks_checked: int
    blocks_passed: int
    blocks_failed: int
    replay_success_rate: float
    determinism_score: float
    ledger_integrity: str


def _hash_state(state: State) -> str:
    return compute_root_hash(serialize_state(state))


def load_scenario(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required = ["name", "epoch", "supply", "participants", "epochs"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Scenario missing required keys: {missing}")

    return data


def build_ledger_for_scenario(scenario: dict, output_root: str = "data/replays") -> str:
    scenario_dir = Path(output_root) / scenario["name"]
    blocks_dir = scenario_dir / "blocks"

    if scenario_dir.exists():
        shutil.rmtree(scenario_dir)
    blocks_dir.mkdir(parents=True, exist_ok=True)

    state = State(
        epoch=int(scenario["epoch"]),
        supply=float(scenario["supply"]),
        participants=int(scenario["participants"]),
    )
    epochs = int(scenario["epochs"])

    store = BlockStore(data_dir=str(blocks_dir))
    for _ in range(epochs):
        state = process_pipeline(state)
        store.append(_hash_state(state))

    return str(blocks_dir)


def run_scenario(path: str, output_root: str = "data/replays") -> ScenarioRunResult:
    scenario = load_scenario(path)
    data_dir = build_ledger_for_scenario(scenario, output_root=output_root)

    initial_state = State(
        epoch=int(scenario["epoch"]),
        supply=float(scenario["supply"]),
        participants=int(scenario["participants"]),
    )

    report = audit_ledger_replay(initial_state=initial_state, data_dir=data_dir)
    return ScenarioRunResult(
        scenario_name=scenario["name"],
        data_dir=data_dir,
        blocks_checked=report.blocks_checked,
        blocks_passed=report.blocks_passed,
        blocks_failed=report.blocks_failed,
        replay_success_rate=report.replay_success_rate,
        determinism_score=report.determinism_score,
        ledger_integrity=report.ledger_integrity,
    )


def run_all_scenarios(scenarios_dir: str = "scenarios", output_root: str = "data/replays") -> dict:
    paths = sorted(Path(scenarios_dir).glob("*.json"))
    if not paths:
        return {
            "scenarios_checked": 0,
            "scenarios_passed": 0,
            "scenarios_failed": 0,
            "blocks_checked": 0,
            "blocks_passed": 0,
            "blocks_failed": 0,
            "replay_success_rate": 0.0,
            "determinism_score": 0.0,
            "ledger_integrity": "PASS",
            "results": [],
        }

    results: list[ScenarioRunResult] = []
    for path in paths:
        results.append(run_scenario(str(path), output_root=output_root))

    scenarios_checked = len(results)
    scenarios_passed = sum(1 for r in results if r.ledger_integrity == "PASS")
    scenarios_failed = scenarios_checked - scenarios_passed

    blocks_checked = sum(r.blocks_checked for r in results)
    blocks_passed = sum(r.blocks_passed for r in results)
    blocks_failed = sum(r.blocks_failed for r in results)
    replay_success_rate = blocks_passed / blocks_checked if blocks_checked else 0.0
    determinism_score = replay_success_rate
    ledger_integrity = "PASS" if scenarios_failed == 0 and blocks_failed == 0 else "FAIL"

    return {
        "scenarios_checked": scenarios_checked,
        "scenarios_passed": scenarios_passed,
        "scenarios_failed": scenarios_failed,
        "blocks_checked": blocks_checked,
        "blocks_passed": blocks_passed,
        "blocks_failed": blocks_failed,
        "replay_success_rate": replay_success_rate,
        "determinism_score": determinism_score,
        "ledger_integrity": ledger_integrity,
        "results": [
            {
                "scenario_name": r.scenario_name,
                "data_dir": r.data_dir,
                "blocks_checked": r.blocks_checked,
                "blocks_passed": r.blocks_passed,
                "blocks_failed": r.blocks_failed,
                "replay_success_rate": r.replay_success_rate,
                "determinism_score": r.determinism_score,
                "ledger_integrity": r.ledger_integrity,
            }
            for r in results
        ],
    }


__all__ = [
    "ScenarioRunResult",
    "load_scenario",
    "build_ledger_for_scenario",
    "run_scenario",
    "run_all_scenarios",
]
