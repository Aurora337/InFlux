#!/usr/bin/env python3
"""Verify minimal testnet health criteria."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify(network_path: Path, expected_validators: int) -> tuple[bool, str]:
    payload = json.loads(network_path.read_text(encoding="utf-8"))
    peers = int(payload.get("peer_count", 0))
    if peers < expected_validators:
        return False, f"Network unhealthy: expected {expected_validators} peers, found {peers}"
    return True, "Network Healthy"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify testnet bootstrap health")
    parser.add_argument(
        "--network",
        default="testnet/bootstrap/network.json",
        help="Path to bootstrap network JSON",
    )
    parser.add_argument(
        "--expected-validators",
        type=int,
        default=5,
        help="Expected peer count",
    )
    args = parser.parse_args()

    ok, message = verify(Path(args.network), args.expected_validators)
    print(message)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
