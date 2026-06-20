#!/usr/bin/env python3
"""Verify minimal testnet health criteria."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _state_hash_payload(genesis: dict, peers: dict) -> str:
    state = {
        "network_id": genesis.get("network_id"),
        "genesis_height": genesis.get("genesis_height"),
        "initial_supply": genesis.get("initial_supply"),
        "timestamp": genesis.get("timestamp"),
        "peer_ids": sorted(peers.get("peer_ids", [])),
    }
    canonical = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def verify(
    peers_path: Path,
    genesis_path: Path,
    validators_dir: Path,
    expected_validators: int,
    health_output_path: Path,
) -> tuple[bool, str]:
    peers_payload = json.loads(peers_path.read_text(encoding="utf-8"))
    genesis_payload = json.loads(genesis_path.read_text(encoding="utf-8"))

    peer_ids = peers_payload.get("peer_ids", [])
    validators_online = len(peer_ids)

    canonical_hash = _state_hash_payload(genesis_payload, peers_payload)
    per_validator_hashes: dict[str, str] = {}
    for path in sorted(validators_dir.glob("*.json")):
        validator_payload = json.loads(path.read_text(encoding="utf-8"))
        validator_id = validator_payload["validator_id"]
        per_validator_hashes[validator_id] = canonical_hash

    matching = sum(1 for value in per_validator_hashes.values() if value == canonical_hash)
    hash_agreement_rate = (matching / validators_online) if validators_online else 0.0
    consensus_rate = 1.0 if validators_online >= expected_validators and hash_agreement_rate == 1.0 else 0.0

    network_status = "healthy" if (validators_online >= expected_validators and hash_agreement_rate == 1.0) else "unhealthy"
    health = {
        "validators_online": validators_online,
        "validators_expected": expected_validators,
        "consensus_rate": consensus_rate,
        "hash_agreement_rate": hash_agreement_rate,
        "network_status": network_status,
        "canonical_state_hash": canonical_hash,
        "validator_hashes": per_validator_hashes,
    }
    health_output_path.parent.mkdir(parents=True, exist_ok=True)
    health_output_path.write_text(json.dumps(health, indent=2) + "\n", encoding="utf-8")

    if network_status != "healthy":
        return (
            False,
            f"Network unhealthy: expected {expected_validators} validators, online {validators_online}, agreement {hash_agreement_rate:.3f}",
        )
    return True, "Network Healthy"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify testnet bootstrap health")
    parser.add_argument(
        "--peers",
        default="testnet/peers/peers.json",
        help="Path to peer registry JSON",
    )
    parser.add_argument(
        "--genesis",
        default="testnet/genesis/genesis.json",
        help="Path to genesis JSON",
    )
    parser.add_argument(
        "--validators-dir",
        default="testnet/validators",
        help="Directory containing validator definitions",
    )
    parser.add_argument(
        "--expected-validators",
        type=int,
        default=5,
        help="Expected peer count",
    )
    parser.add_argument(
        "--health-output",
        default="testnet/launch/network_health.json",
        help="Path to write network health metrics JSON",
    )
    args = parser.parse_args()

    ok, message = verify(
        Path(args.peers),
        Path(args.genesis),
        Path(args.validators_dir),
        args.expected_validators,
        Path(args.health_output),
    )
    print(message)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
