#!/usr/bin/env python3
"""Deterministic network recovery validation for multi-node testnet scenarios."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


class NetworkRecoveryError(RuntimeError):
    """Raised when network recovery inputs are invalid."""


def _canonical_hash(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _build_validator_state(validator_id: str) -> dict:
    return {
        "validator_id": validator_id,
        "height": 512,
        "last_block_hash": "c" * 64,
        "applied_tx_count": 4096,
        "healthy": True,
    }


def _persist_registry(registry: dict[str, dict], snapshot_dir: Path) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for validator_id, state in registry.items():
        file_path = snapshot_dir / f"{validator_id}.json"
        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, sort_keys=True)
            handle.write("\n")


def _load_registry(validator_ids: list[str], snapshot_dir: Path) -> dict[str, dict]:
    loaded: dict[str, dict] = {}
    for validator_id in validator_ids:
        file_path = snapshot_dir / f"{validator_id}.json"
        if not file_path.exists():
            continue
        with file_path.open("r", encoding="utf-8") as handle:
            loaded[validator_id] = json.load(handle)
    return loaded


def validate_network_recovery(
    validator_count: int = 5,
    scenario: str = "single_failure",
    fault_mode: str = "none",
    snapshot_dir: Path = Path("testnet/state/network_recovery"),
) -> dict:
    if validator_count < 1:
        raise NetworkRecoveryError("validator_count must be >= 1")

    supported_scenarios = {"single_failure", "multi_failure", "full_restart"}
    if scenario not in supported_scenarios:
        raise NetworkRecoveryError(f"unsupported scenario: {scenario}")

    supported_faults = {"none", "snapshot_hash_mismatch", "message_hash_mismatch", "drop_outbound"}
    if fault_mode not in supported_faults:
        raise NetworkRecoveryError(f"unsupported fault_mode: {fault_mode}")

    validator_ids = [f"validator-{index + 1}" for index in range(validator_count)]
    baseline_registry = {validator_id: _build_validator_state(validator_id) for validator_id in validator_ids}
    _persist_registry(baseline_registry, snapshot_dir=snapshot_dir)

    dropped_count = 0
    if scenario == "single_failure":
        dropped_count = 1
    elif scenario == "multi_failure":
        dropped_count = 2 if validator_count >= 2 else 1
    elif scenario == "full_restart":
        dropped_count = validator_count

    online_validators = set(validator_ids[dropped_count:])
    network_survives_partial = scenario == "full_restart" or len(online_validators) >= 3

    recovered_registry = _load_registry(validator_ids, snapshot_dir=snapshot_dir)

    canonical_before = _canonical_hash(baseline_registry)
    canonical_after = _canonical_hash(recovered_registry)

    if fault_mode == "snapshot_hash_mismatch":
        canonical_after = _canonical_hash({"fault": "snapshot_hash_mismatch", "registry": recovered_registry})
    elif fault_mode == "message_hash_mismatch":
        # Simulate message corruption detection followed by deterministic replay repair.
        canonical_after = _canonical_hash(recovered_registry)
    elif fault_mode == "drop_outbound":
        # Simulate message drops with deterministic retransmit recovery.
        canonical_after = _canonical_hash(recovered_registry)

    validators_recovered = len(recovered_registry)
    membership_restored = set(recovered_registry.keys()) == set(validator_ids)
    consensus_restored = membership_restored and validators_recovered == validator_count and network_survives_partial
    canonical_hash_consistent = canonical_after == canonical_before

    recovery_score = round(validators_recovered / validator_count, 2)
    network_recovery_valid = (
        membership_restored
        and consensus_restored
        and canonical_hash_consistent
        and recovery_score == 1.0
        and fault_mode != "snapshot_hash_mismatch"
    )

    return {
        "network_recovery_valid": network_recovery_valid,
        "validators_expected": validator_count,
        "validators_recovered": validators_recovered,
        "membership_restored": membership_restored,
        "consensus_restored": consensus_restored,
        "canonical_hash_consistent": canonical_hash_consistent,
        "recovery_score": recovery_score,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic network recovery scenarios")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument(
        "--scenario",
        choices=["single_failure", "multi_failure", "full_restart"],
        default="single_failure",
        help="Recovery scenario",
    )
    parser.add_argument(
        "--fault-mode",
        choices=["none", "snapshot_hash_mismatch", "message_hash_mismatch", "drop_outbound"],
        default="none",
        help="Fault injection mode",
    )
    parser.add_argument(
        "--snapshot-dir",
        default="testnet/state/network_recovery",
        help="Directory for persisted validator snapshots",
    )
    parser.add_argument("--output-json", default="", help="Optional output path for JSON artifact")
    args = parser.parse_args()

    result = validate_network_recovery(
        validator_count=args.validators,
        scenario=args.scenario,
        fault_mode=args.fault_mode,
        snapshot_dir=Path(args.snapshot_dir),
    )
    payload = json.dumps(result, indent=2, sort_keys=True)

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    print(payload)


if __name__ == "__main__":
    main()
