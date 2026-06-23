#!/usr/bin/env python3
"""Deterministic node restart and recovery validation for testnet hardening."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


class NodeRecoveryError(RuntimeError):
    """Raised when node recovery validation inputs are invalid."""


def _build_node_state(node_id: str) -> dict:
    return {
        "node_id": node_id,
        "height": 300,
        "last_block_hash": "b" * 64,
        "applied_tx_count": 2048,
        "healthy": True,
    }


def _canonical_hash(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _persist_snapshot(node_state: dict, snapshot_dir: Path) -> Path:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / f"{node_state['node_id']}.json"
    with snapshot_path.open("w", encoding="utf-8") as handle:
        json.dump(node_state, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return snapshot_path


def _load_snapshot(snapshot_path: Path) -> dict | None:
    if not snapshot_path.exists():
        return None
    try:
        with snapshot_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return None


def validate_node_recovery(
    node_count: int = 5,
    snapshot_dir: Path = Path("testnet/state"),
    fault_mode: str = "none",
    restart_delay_ms: int = 0,
) -> dict:
    if node_count < 1:
        raise NodeRecoveryError("node_count must be >= 1")
    if restart_delay_ms < 0:
        raise NodeRecoveryError("restart_delay_ms must be >= 0")

    supported_faults = {"none", "unexpected_shutdown", "missing_snapshot", "corrupted_snapshot", "delayed_restart"}
    if fault_mode not in supported_faults:
        raise NodeRecoveryError(f"unsupported fault_mode: {fault_mode}")

    node_ids = [f"validator-{index + 1}" for index in range(node_count)]
    original_states: dict[str, dict] = {}

    for node_id in node_ids:
        state = _build_node_state(node_id)
        original_states[node_id] = state
        _persist_snapshot(state, snapshot_dir=snapshot_dir)

    if fault_mode == "missing_snapshot":
        (snapshot_dir / "validator-1.json").unlink(missing_ok=True)
    elif fault_mode == "corrupted_snapshot":
        (snapshot_dir / "validator-1.json").write_text("{\n  invalid-json\n", encoding="utf-8")

    restart_delay_applied = restart_delay_ms if fault_mode == "delayed_restart" else 0

    recovered_states: dict[str, dict] = {}
    missing_snapshot_detected = False
    corrupted_snapshot_detected = False

    for node_id in node_ids:
        loaded = _load_snapshot(snapshot_dir / f"{node_id}.json")
        if loaded is None:
            if (snapshot_dir / f"{node_id}.json").exists():
                corrupted_snapshot_detected = True
            else:
                missing_snapshot_detected = True
            continue
        recovered_states[node_id] = loaded

    expected_peers = set(node_ids)
    recovered_peers = set(recovered_states.keys())

    state_restored = recovered_states == original_states
    original_hashes = {node_id: _canonical_hash(state) for node_id, state in original_states.items()}
    recovered_hashes = {node_id: _canonical_hash(state) for node_id, state in recovered_states.items()}
    hash_consistent = recovered_hashes == original_hashes

    peer_membership_restored = recovered_peers == expected_peers
    restart_success_rate = round(len(recovered_states) / node_count, 2)

    recovery_valid = (
        state_restored
        and hash_consistent
        and peer_membership_restored
        and restart_success_rate == 1.0
        and not missing_snapshot_detected
        and not corrupted_snapshot_detected
    )

    return {
        "recovery_valid": recovery_valid,
        "restart_success_rate": restart_success_rate,
        "state_restored": state_restored,
        "hash_consistent": hash_consistent,
        "peer_membership_restored": peer_membership_restored,
        "missing_snapshot_detected": missing_snapshot_detected,
        "corrupted_snapshot_detected": corrupted_snapshot_detected,
        "restart_delay_applied_ms": restart_delay_applied,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic node restart and recovery")
    parser.add_argument("--node-count", type=int, default=5, help="Number of validator nodes")
    parser.add_argument("--snapshot-dir", default="testnet/state", help="Directory for persisted node snapshots")
    parser.add_argument(
        "--fault-mode",
        default="none",
        choices=["none", "unexpected_shutdown", "missing_snapshot", "corrupted_snapshot", "delayed_restart"],
        help="Fault scenario to validate",
    )
    parser.add_argument("--restart-delay-ms", type=int, default=0, help="Deterministic restart delay metric")
    parser.add_argument("--output-json", default="", help="Optional output path for JSON artifact")
    args = parser.parse_args()

    result = validate_node_recovery(
        node_count=args.node_count,
        snapshot_dir=Path(args.snapshot_dir),
        fault_mode=args.fault_mode,
        restart_delay_ms=args.restart_delay_ms,
    )
    payload = json.dumps(result, indent=2, sort_keys=True)

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    print(payload)


if __name__ == "__main__":
    main()
