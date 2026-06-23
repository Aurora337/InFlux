"""Adversarial and fault-injection harness for multi-node consensus resilience."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import sys

sys.path.insert(0, "src")

from influx.kernel.state import State
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash
from influx.kernel.sync.shcm import verify_state_hash


@dataclass
class FaultRoundResult:
    round_index: int
    canonical_hash: str
    network_hash: str
    consensus_passed: bool
    agreement_rate: float
    replay_match: bool
    had_fault: bool


def _hash_state(state: State) -> str:
    return compute_root_hash(serialize_state(state))


def _select_majority_hash(peer_hashes: list[str]) -> str:
    counts = Counter(peer_hashes)
    return counts.most_common(1)[0][0]


def load_fault_scenario(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        scenario = json.load(f)

    required = ["name", "validators", "rounds", "initial_state", "events"]
    missing = [key for key in required if key not in scenario]
    if missing:
        raise ValueError(f"Fault scenario missing keys: {missing}")

    return scenario


def run_fault_injection_scenario(path: str) -> dict:
    scenario = load_fault_scenario(path)

    validators = scenario["validators"]
    rounds = int(scenario["rounds"])
    initial = scenario["initial_state"]
    events = scenario["events"]

    events_by_round: dict[int, list[dict]] = defaultdict(list)
    for event in events:
        events_by_round[int(event["round"])].append(event)

    current_state = State(
        epoch=int(initial["epoch"]),
        supply=float(initial["supply"]),
        participants=int(initial["participants"]),
    )

    divergence_count = {validator: 0 for validator in validators}
    recovery_events = 0
    fault_rounds = 0
    results: list[FaultRoundResult] = []

    previous_network_hash = _hash_state(current_state)

    for round_index in range(1, rounds + 1):
        next_state = process_pipeline(current_state)
        canonical_hash = _hash_state(next_state)

        local_hashes: dict[str, str | None] = {validator: canonical_hash for validator in validators}

        round_events = events_by_round.get(round_index, [])
        had_fault = len(round_events) > 0
        if had_fault:
            fault_rounds += 1

        for event in round_events:
            event_type = event["type"]
            if event_type == "validator_dropout":
                target = event["validator"]
                local_hashes[target] = None
            elif event_type == "stale_validator":
                target = event["validator"]
                local_hashes[target] = previous_network_hash
            elif event_type == "corrupted_hash":
                target = event["validator"]
                local_hashes[target] = f"corrupt-{target}-{round_index}"
            elif event_type == "network_partition":
                for target in event.get("validators", []):
                    local_hashes[target] = f"partition-{round_index}-{target}"
            elif event_type == "late_block":
                target = event["validator"]
                local_hashes[target] = _hash_state(current_state)
            elif event_type == "invalid_state":
                target = event["validator"]
                invalid_state = State(
                    epoch=next_state.epoch,
                    supply=next_state.supply + 1.0,
                    participants=max(1, next_state.participants - 1),
                )
                local_hashes[target] = _hash_state(invalid_state)

        peer_hashes = [value for value in local_hashes.values() if value is not None]
        if not peer_hashes:
            network_hash = ""
            consensus_passed = False
            agreement_rate = 0.0
            replay_match = False
        else:
            network_hash = _select_majority_hash(peer_hashes)
            consensus_passed = verify_state_hash(network_hash, peer_hashes)
            agreement_rate = sum(1 for value in peer_hashes if value == network_hash) / len(peer_hashes)
            replay_match = network_hash == canonical_hash

        for validator in validators:
            validator_hash = local_hashes[validator]
            if validator_hash is None or validator_hash != network_hash:
                divergence_count[validator] += 1

        if had_fault and consensus_passed and replay_match:
            recovery_events += 1

        if consensus_passed and replay_match:
            current_state = next_state

        previous_network_hash = network_hash or previous_network_hash

        results.append(
            FaultRoundResult(
                round_index=round_index,
                canonical_hash=canonical_hash,
                network_hash=network_hash,
                consensus_passed=consensus_passed,
                agreement_rate=agreement_rate,
                replay_match=replay_match,
                had_fault=had_fault,
            )
        )

    rounds_passed = sum(1 for result in results if result.consensus_passed)
    rounds_failed = rounds - rounds_passed
    consensus_agreement_rate = (
        sum(result.agreement_rate for result in results) / len(results)
        if results else 0.0
    )
    replay_success_rate = (
        sum(1 for result in results if result.replay_match) / len(results)
        if results else 0.0
    )
    recovery_rate = (recovery_events / fault_rounds) if fault_rounds else 1.0

    return {
        "scenario": scenario["name"],
        "validators": validators,
        "rounds_checked": rounds,
        "rounds_passed": rounds_passed,
        "rounds_failed": rounds_failed,
        "agreement_rate": consensus_agreement_rate,
        "recovery_rate": recovery_rate,
        "replay_success_rate": replay_success_rate,
        "divergence_count": divergence_count,
        "fault_rounds": fault_rounds,
        "fault_recovered": recovery_events,
        "final_epoch": current_state.epoch,
        "final_state_hash": _hash_state(current_state),
        "details": [
            {
                "round": item.round_index,
                "canonical_hash": item.canonical_hash,
                "network_hash": item.network_hash,
                "consensus_passed": item.consensus_passed,
                "agreement_rate": item.agreement_rate,
                "replay_match": item.replay_match,
                "had_fault": item.had_fault,
            }
            for item in results
        ],
    }


def run_fault_suite(scenarios_dir: str = "scenarios/fault") -> dict:
    from pathlib import Path

    paths = sorted(Path(scenarios_dir).glob("*.json"))
    if not paths:
        return {
            "scenarios_checked": 0,
            "scenarios_passed": 0,
            "scenarios_failed": 0,
            "agreement_rate": 0.0,
            "recovery_rate": 0.0,
            "replay_success_rate": 0.0,
            "results": [],
        }

    results = [run_fault_injection_scenario(str(path)) for path in paths]

    scenarios_checked = len(results)
    scenarios_passed = sum(1 for result in results if result["rounds_failed"] == 0)
    scenarios_failed = scenarios_checked - scenarios_passed

    agreement_rate = sum(result["agreement_rate"] for result in results) / scenarios_checked
    recovery_rate = sum(result["recovery_rate"] for result in results) / scenarios_checked
    replay_success_rate = sum(result["replay_success_rate"] for result in results) / scenarios_checked

    return {
        "scenarios_checked": scenarios_checked,
        "scenarios_passed": scenarios_passed,
        "scenarios_failed": scenarios_failed,
        "agreement_rate": agreement_rate,
        "recovery_rate": recovery_rate,
        "replay_success_rate": replay_success_rate,
        "results": results,
    }


__all__ = ["load_fault_scenario", "run_fault_injection_scenario", "run_fault_suite"]
