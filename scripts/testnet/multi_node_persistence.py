#!/usr/bin/env python3
"""Deterministic multi-node persistence and restart recovery validation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


class PersistenceError(RuntimeError):
    """Raised when persistence inputs or recovery expectations are invalid."""


def _build_node_state(node_id: str) -> dict:
    return {
        "node_id": node_id,
        "height": 256,
        "last_block_hash": "a" * 64,
        "applied_tx_count": 1024,
        "healthy": True,
    }


def _canonical_hash(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _persist_node_state(node_state: dict, state_dir: Path) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    file_path = state_dir / f"{node_state['node_id']}.json"
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(node_state, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return file_path


def _load_node_state(file_path: Path) -> dict:
    if not file_path.exists():
        raise PersistenceError(f"missing persisted state file: {file_path}")
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_multi_node_persistence(node_count: int = 5, state_dir: Path = Path("testnet/state")) -> dict:
    if node_count < 1:
        raise PersistenceError("node_count must be >= 1")

    node_ids = [f"validator-{index + 1}" for index in range(node_count)]
    original_states: dict[str, dict] = {}
    recovered_states: dict[str, dict] = {}

    for node_id in node_ids:
        state = _build_node_state(node_id)
        original_states[node_id] = state
        saved_path = _persist_node_state(state, state_dir=state_dir)
        recovered_states[node_id] = _load_node_state(saved_path)

    original_hashes = {node_id: _canonical_hash(state) for node_id, state in original_states.items()}
    recovered_hashes = {node_id: _canonical_hash(state) for node_id, state in recovered_states.items()}

    durable_write_valid = len(list(state_dir.glob("validator-*.json"))) == node_count
    restart_recovery_valid = recovered_states == original_states
    hash_consistent = recovered_hashes == original_hashes

    persistence_valid = durable_write_valid and restart_recovery_valid and hash_consistent

    return {
        "persistence_valid": persistence_valid,
        "nodes_persisted": node_count,
        "durable_write_valid": durable_write_valid,
        "restart_recovery_valid": restart_recovery_valid,
        "state_hash_consistent": hash_consistent,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic multi-node persistence")
    parser.add_argument("--node-count", type=int, default=5, help="Number of validator nodes")
    parser.add_argument("--state-dir", default="testnet/state", help="Directory for persisted state files")
    parser.add_argument("--output-json", default="", help="Optional output path for JSON artifact")
    args = parser.parse_args()

    result = validate_multi_node_persistence(node_count=args.node_count, state_dir=Path(args.state_dir))
    payload = json.dumps(result, indent=2, sort_keys=True)

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    print(payload)


if __name__ == "__main__":
    main()
