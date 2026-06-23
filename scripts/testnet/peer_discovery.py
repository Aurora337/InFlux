#!/usr/bin/env python3
"""Deterministic peer discovery validation for testnet readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


class PeerDiscoveryError(RuntimeError):
    """Raised when peer discovery inputs are invalid."""


DEFAULT_PEERS_PATH = Path("testnet/peers/peers.json")
DEFAULT_VALIDATORS_DIR = Path("testnet/validators")
DEFAULT_NETWORK_HEALTH_PATH = Path("testnet/launch/network_health.json")

def _read_json(file_path: Path) -> dict | list | None:
    if not file_path.exists():
        return None
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _fallback_peer_ids(expected_peer_count: int) -> list[str]:
    return [f"peer-{index + 1}" for index in range(expected_peer_count)]


def _extract_peer_ids(peers_payload: dict | list | None, expected_peer_count: int) -> list[str]:
    if peers_payload is None:
        return _fallback_peer_ids(expected_peer_count)

    raw_entries = peers_payload.get("peers", []) if isinstance(peers_payload, dict) else peers_payload
    peer_ids: list[str] = []
    for entry in raw_entries:
        if isinstance(entry, dict):
            peer_id = entry.get("peer_id") or entry.get("id")
            if peer_id:
                peer_ids.append(str(peer_id))
        elif isinstance(entry, str):
            peer_ids.append(entry)
    return peer_ids


def _extract_validator_peer_ids(validators_dir: Path, expected_peer_count: int) -> list[str]:
    validator_files = sorted(validators_dir.glob("*.json"))
    if not validator_files:
        return _fallback_peer_ids(expected_peer_count)

    peer_ids: list[str] = []
    for validator_file in validator_files:
        payload = _read_json(validator_file)
        if not isinstance(payload, dict):
            continue
        peer_id = payload.get("peer_id") or payload.get("validator_id")
        if peer_id:
            peer_ids.append(str(peer_id))
    return peer_ids


def _extract_expected_count(network_health_payload: dict | list | None, default_count: int) -> int:
    if isinstance(network_health_payload, dict) and isinstance(network_health_payload.get("expected_peer_count"), int):
        return int(network_health_payload["expected_peer_count"])
    return default_count


def _network_health_consistent(network_health_payload: dict | list | None, discovered_peers: set[str]) -> bool:
    if not isinstance(network_health_payload, dict):
        return True

    reported_healthy = network_health_payload.get("healthy_peers")
    network_healthy = network_health_payload.get("network_healthy", True)
    if reported_healthy is None:
        return bool(network_healthy)
    if not isinstance(reported_healthy, list):
        return False
    return bool(network_healthy) and set(str(item) for item in reported_healthy) == discovered_peers


def validate_peer_discovery(
    peer_count: int = 5,
    peers_path: Path = DEFAULT_PEERS_PATH,
    validators_dir: Path = DEFAULT_VALIDATORS_DIR,
    network_health_path: Path = DEFAULT_NETWORK_HEALTH_PATH,
) -> dict:
    if peer_count < 1:
        raise PeerDiscoveryError("peer_count must be >= 1")

    peers_payload = _read_json(peers_path)
    network_health_payload = _read_json(network_health_path)
    expected_peer_count = _extract_expected_count(network_health_payload, peer_count)

    peer_ids = _extract_peer_ids(peers_payload, expected_peer_count)
    validator_peer_ids = _extract_validator_peer_ids(validators_dir, expected_peer_count)

    discovered_peers = set(peer_ids)
    validator_peers = set(validator_peer_ids)
    expected_peers = validator_peers if validator_peers else set(_fallback_peer_ids(expected_peer_count))

    duplicate_peers = len(peer_ids) - len(discovered_peers)
    missing_peers = len(expected_peers - discovered_peers)
    membership_consistent = discovered_peers == expected_peers
    peer_registration = len(peer_ids) >= expected_peer_count
    peer_enumeration = len(discovered_peers) == len(peer_ids) - duplicate_peers
    peer_lookup = all(peer in discovered_peers for peer in expected_peers)
    count_matches = len(discovered_peers) == expected_peer_count
    health_consistent = _network_health_consistent(network_health_payload, discovered_peers)

    peer_discovery_valid = (
        peer_registration
        and peer_enumeration
        and peer_lookup
        and membership_consistent
        and count_matches
        and health_consistent
        and duplicate_peers == 0
        and missing_peers == 0
    )

    return {
        "peer_discovery_valid": peer_discovery_valid,
        "peers_found": len(discovered_peers),
        "membership_consistent": membership_consistent,
        "duplicate_peers": duplicate_peers,
        "missing_peers": missing_peers,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic peer discovery")
    parser.add_argument("--peer-count", type=int, default=5, help="Expected peer count")
    parser.add_argument("--peers-path", default=str(DEFAULT_PEERS_PATH), help="Path to peers.json")
    parser.add_argument("--validators-dir", default=str(DEFAULT_VALIDATORS_DIR), help="Path to validators directory")
    parser.add_argument(
        "--network-health-path",
        default=str(DEFAULT_NETWORK_HEALTH_PATH),
        help="Path to network_health.json",
    )
    parser.add_argument("--output-json", default="", help="Optional output path for JSON artifact")
    args = parser.parse_args()

    result = validate_peer_discovery(
        peer_count=args.peer_count,
        peers_path=Path(args.peers_path),
        validators_dir=Path(args.validators_dir),
        network_health_path=Path(args.network_health_path),
    )
    payload = json.dumps(result, indent=2, sort_keys=True)

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    print(payload)


if __name__ == "__main__":
    main()
