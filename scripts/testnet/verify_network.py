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
        "epoch": genesis.get("epoch", 1),
        "peer_ids": sorted(peers.get("peer_ids", [])),
    }
    canonical = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _load_snapshots(snapshots_dir: Path) -> dict[str, dict]:
    snapshots: dict[str, dict] = {}
    for path in sorted(snapshots_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        validator_id = payload.get("validator_id")
        if validator_id:
            snapshots[validator_id] = payload
    return snapshots


def _load_messages(messages_dir: Path) -> list[dict]:
    messages: list[dict] = []
    for path in sorted(messages_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        messages.append(payload)
    return messages


def _validate_messages(
    messages: list[dict],
    snapshots: dict[str, dict],
    expected_validators: int,
) -> tuple[int, int, float, int, int]:
    expected_count = expected_validators * (expected_validators - 1)
    valid = 0
    invalid = 0

    for message in messages:
        from_id = message.get("from")
        to_id = message.get("to")
        msg_type = message.get("message_type")
        msg_hash = message.get("state_hash")

        if not from_id or not to_id or from_id == to_id:
            invalid += 1
            continue
        if msg_type != "STATE_SYNC":
            invalid += 1
            continue
        sender_snapshot = snapshots.get(from_id)
        if not sender_snapshot:
            invalid += 1
            continue
        if sender_snapshot.get("state_hash") != msg_hash:
            invalid += 1
            continue
        valid += 1

    completion_rate = (valid / expected_count) if expected_count else 0.0
    missing = max(expected_count - valid, 0)
    return valid, expected_count, completion_rate, invalid, missing


def verify(
    peers_path: Path,
    genesis_path: Path,
    snapshots_dir: Path,
    messages_dir: Path,
    expected_validators: int,
    epoch: int,
    health_output_path: Path,
) -> tuple[bool, str]:
    peers_payload = json.loads(peers_path.read_text(encoding="utf-8"))
    genesis_payload = json.loads(genesis_path.read_text(encoding="utf-8"))
    genesis_payload["epoch"] = epoch

    peer_ids = peers_payload.get("peer_ids", [])
    validators_online = len(peer_ids)

    canonical_hash = _state_hash_payload(genesis_payload, peers_payload)
    snapshots = _load_snapshots(snapshots_dir)
    messages = _load_messages(messages_dir)
    per_validator_hashes: dict[str, str] = {
        validator_id: payload.get("state_hash", "")
        for validator_id, payload in snapshots.items()
    }

    (
        valid_messages,
        expected_message_count,
        handshake_completion_rate,
        invalid_message_count,
        missing_message_count,
    ) = _validate_messages(
        messages,
        snapshots,
        expected_validators,
    )

    hash_counts: dict[str, int] = {}
    for value in per_validator_hashes.values():
        hash_counts[value] = hash_counts.get(value, 0) + 1
    most_common_count = max(hash_counts.values()) if hash_counts else 0

    matching = sum(1 for value in per_validator_hashes.values() if value == canonical_hash)
    hash_agreement_rate = (matching / validators_online) if validators_online else 0.0
    agreement_rate = (most_common_count / validators_online) if validators_online else 0.0
    divergence_count = validators_online - most_common_count
    consensus_status = (
        "established"
        if (
            validators_online >= expected_validators
            and agreement_rate == 1.0
            and hash_agreement_rate == 1.0
            and handshake_completion_rate == 1.0
        )
        else "degraded"
    )
    consensus_rate = agreement_rate

    network_status = (
        "healthy"
        if (
            validators_online >= expected_validators
            and agreement_rate == 1.0
            and hash_agreement_rate == 1.0
            and handshake_completion_rate == 1.0
        )
        else "unhealthy"
    )
    health = {
        "validators_online": validators_online,
        "validators_expected": expected_validators,
        "consensus_rate": consensus_rate,
        "hash_agreement_rate": hash_agreement_rate,
        "agreement_rate": agreement_rate,
        "divergence_count": divergence_count,
        "consensus_status": consensus_status,
        "message_count": valid_messages,
        "expected_message_count": expected_message_count,
        "handshake_completion_rate": handshake_completion_rate,
        "invalid_message_count": invalid_message_count,
        "missing_message_count": missing_message_count,
        "network_status": network_status,
        "canonical_state_hash": canonical_hash,
        "validator_hashes": per_validator_hashes,
    }
    health_output_path.parent.mkdir(parents=True, exist_ok=True)
    health_output_path.write_text(json.dumps(health, indent=2) + "\n", encoding="utf-8")

    if network_status != "healthy":
        return (
            False,
            f"Network unhealthy: expected {expected_validators} validators, online {validators_online}, agreement {agreement_rate:.3f}",
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
        "--snapshots-dir",
        default="testnet/launch/snapshots",
        help="Directory containing validator state snapshots",
    )
    parser.add_argument(
        "--messages-dir",
        default="testnet/messages",
        help="Directory containing validator STATE_SYNC messages",
    )
    parser.add_argument(
        "--expected-validators",
        type=int,
        default=5,
        help="Expected peer count",
    )
    parser.add_argument(
        "--epoch",
        type=int,
        default=1,
        help="Expected snapshot epoch",
    )
    parser.add_argument(
        "--health-output",
        default="testnet/launch/network_health.json",
        help="Path to write network health metrics JSON",
    )
    parser.add_argument(
        "--allow-unhealthy",
        action="store_true",
        help="Return success exit code even when network is unhealthy",
    )
    args = parser.parse_args()

    ok, message = verify(
        Path(args.peers),
        Path(args.genesis),
        Path(args.snapshots_dir),
        Path(args.messages_dir),
        args.expected_validators,
        args.epoch,
        Path(args.health_output),
    )
    print(message)
    if ok or args.allow_unhealthy:
        raise SystemExit(0)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
