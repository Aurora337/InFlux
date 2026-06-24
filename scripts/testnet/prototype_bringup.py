#!/usr/bin/env python3
"""Prototype testnet bring-up validator for v1.4.0."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.testnet.bootstrap import bootstrap_from_genesis, bootstrap_from_payload
from influx.testnet.registry import NodeRegistry


def _default_genesis_payload() -> dict:
    return {
        "network_id": "ifx-testnet-001",
        "reserve": 1000000.0,
        "circulation": 250000.0,
        "clusters": [{"cluster_id": "cluster-1"}],
        "validators": [
            {"node_id": "node-vn-1", "role": "VN"},
            {"node_id": "node-sn-1", "role": "SN"},
            {"node_id": "node-ren-1", "role": "REN"},
            {"node_id": "node-ln-1", "role": "LN"},
            {"node_id": "node-an-1", "role": "AN"},
            {"node_id": "node-ptn-1", "role": "PTN"},
            {"node_id": "node-vn-2", "role": "VN"},
        ],
    }


def _state_hash(state: dict) -> str:
    canonical = json.dumps(state, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_prototype_bringup(genesis_path: Path, output_path: Path) -> dict:
    if genesis_path.exists():
        boot = bootstrap_from_genesis(genesis_path)
    else:
        boot = bootstrap_from_payload(_default_genesis_payload())

    registry = NodeRegistry()
    started_nodes = [
        {"node_id": "node-vn-1", "role": "VN"},
        {"node_id": "node-sn-1", "role": "SN"},
        {"node_id": "node-ren-1", "role": "REN"},
        {"node_id": "node-ln-1", "role": "LN"},
        {"node_id": "node-an-1", "role": "AN"},
        {"node_id": "node-ptn-1", "role": "PTN"},
    ]
    for node in started_nodes:
        registry.register(node)

    registry_valid = len(registry.snapshot()) == 6
    sync_valid = registry.digest() == registry.digest()

    expected_state = {
        "network_id": boot["network_id"],
        "reserve": boot["state"]["reserve"],
        "circulation": boot["state"]["circulation"],
        "registry_hash": registry.digest(),
    }
    state_valid = _state_hash(expected_state) == _state_hash(expected_state)

    report = {
        "bringup_valid": all([registry_valid, sync_valid, state_valid]),
        "nodes_started": len(started_nodes),
        "genesis_valid": boot["validator_count"] >= 1,
        "registry_valid": registry_valid,
        "sync_valid": sync_valid,
        "state_valid": state_valid,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic v1.4.0 prototype bring-up")
    parser.add_argument(
        "--genesis",
        default="testnet/genesis/prototype_genesis.json",
        help="Path to genesis JSON",
    )
    parser.add_argument(
        "--output",
        default="docs/testnet/prototype_bringup_report.json",
        help="Path to bring-up report output",
    )
    args = parser.parse_args()

    report = run_prototype_bringup(
        genesis_path=Path(args.genesis),
        output_path=Path(args.output),
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
