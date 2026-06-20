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


def emit_snapshots(genesis_path: Path, peers_path: Path, output_dir: Path, epoch: int) -> list[Path]:
    genesis = json.loads(genesis_path.read_text(encoding="utf-8"))
    peers = json.loads(peers_path.read_text(encoding="utf-8"))
    peer_ids = peers.get("peer_ids", [])

    state_hash = _shared_state_hash(genesis, peers, epoch)

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for validator_id in peer_ids:
        snapshot = {
            "validator_id": validator_id,
            "epoch": epoch,
            "state_hash": state_hash,
            "timestamp": genesis.get("timestamp"),
            "message_type": "STATE_SYNC",
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
    args = parser.parse_args()

    generated = emit_snapshots(
        genesis_path=Path(args.genesis),
        peers_path=Path(args.peers),
        output_dir=Path(args.output_dir),
        epoch=args.epoch,
    )
    print(f"Emitted snapshots: {len(generated)}")


if __name__ == "__main__":
    main()
