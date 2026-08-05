#!/usr/bin/env python3
"""Emit deterministic validator state snapshots for local state exchange simulation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _shared_state_hash(genesis: dict, peers: dict, epoch: int) -> str:
    payload = {
        "network_id": genesis.get("network_id"),
        "genesis_height": genesis.get("genesis_height"),
        "initial_supply": genesis.get("initial_supply"),
        "timestamp": genesis.get("timestamp"),
        "epoch": epoch,
        "peer_ids": sorted(peers.get("peer_ids", [])),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def emit_snapshots(
    genesis_path: Path,
    peers_path: Path,
    output_dir: Path,
    epoch: int,
    fault_mode: str,
    fault_validator: str,
) -> list[Path]:
    genesis = json.loads(genesis_path.read_text(encoding="utf-8"))
    peers = json.loads(peers_path.read_text(encoding="utf-8"))
    peer_ids = peers.get("peer_ids", [])

    state_hash = _shared_state_hash(genesis, peers, epoch)

    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("*.json"):
        stale.unlink()

    generated: list[Path] = []
    for validator_id in peer_ids:
        snapshot_hash = state_hash
        fault_injected = False
        if fault_mode == "snapshot_hash_mismatch" and fault_validator and validator_id == fault_validator:
            snapshot_hash = hashlib.sha256(f"fault::{state_hash}".encode("utf-8")).hexdigest()
            fault_injected = True

        snapshot = {
            "validator_id": validator_id,
            "epoch": epoch,
            "state_hash": snapshot_hash,
            "timestamp": genesis.get("timestamp"),
            "message_type": "STATE_SYNC",
            "fault_injected": fault_injected,
        }
        path = output_dir / f"{validator_id}.json"
        path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        generated.append(path)
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit deterministic validator state snapshots")
    parser.add_argument("--genesis", default="testnet/genesis/genesis.json", help="Path to genesis JSON")
    parser.add_argument("--peers", default="testnet/peers/peers.json", help="Path to peer registry JSON")
    parser.add_argument("--output-dir", default="testnet/launch/snapshots", help="Snapshot output directory")
    parser.add_argument("--epoch", type=int, default=1, help="Snapshot epoch")
    parser.add_argument(
        "--fault-mode",
        choices=["none", "snapshot_hash_mismatch"],
        default="none",
        help="Optional snapshot fault injection mode",
    )
    parser.add_argument(
        "--fault-validator",
        default="",
        help="Validator id to inject snapshot fault into",
    )
    args = parser.parse_args()

    generated = emit_snapshots(
        genesis_path=Path(args.genesis),
        peers_path=Path(args.peers),
        output_dir=Path(args.output_dir),
        epoch=args.epoch,
        fault_mode=args.fault_mode,
        fault_validator=args.fault_validator,
    )
    print(f"Emitted snapshots: {len(generated)}")


if __name__ == "__main__":
    main()
