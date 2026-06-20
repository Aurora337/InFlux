#!/usr/bin/env python3
"""Generate a deterministic testnet genesis artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_GENESIS = {
    "network_id": "influx-testnet",
    "genesis_height": 0,
    "initial_supply": 77000000,
    "timestamp": 1781913600,
    "validators": [],
}


def generate_genesis(output_path: Path, validator_count: int, timestamp: int) -> dict:
    payload = dict(DEFAULT_GENESIS)
    payload["validator_count"] = validator_count
    payload["timestamp"] = timestamp
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate genesis configuration")
    parser.add_argument(
        "--output",
        default="testnet/genesis/genesis.json",
        help="Path to write genesis JSON",
    )
    parser.add_argument(
        "--validators",
        type=int,
        default=5,
        help="Number of validators in initial testnet",
    )
    parser.add_argument(
        "--timestamp",
        type=int,
        default=1781913600,
        help="Deterministic genesis timestamp",
    )
    args = parser.parse_args()

    payload = generate_genesis(Path(args.output), args.validators, args.timestamp)
    print(f"Generated genesis: {args.output}")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
