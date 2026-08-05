#!/usr/bin/env python3
"""Create validator configuration files for testnet bootstrapping."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _deterministic_public_key(validator_id: str) -> str:
    seed = f"influx-testnet::{validator_id}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()


def create_validator(name: str, host: str, port: int, output_dir: Path, stake: int) -> Path:
    payload = {
        "validator_id": name.lower(),
        "role": "VN",
        "stake": stake,
        "address": f"{host}:{port}",
        "public_key": _deterministic_public_key(name.lower()),
        "status": "created",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{name}.json"
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path


def create_validator_registry(count: int, host: str, start_port: int, stake: int, output_dir: Path) -> list[Path]:
    created = []
    for idx in range(1, count + 1):
        name = f"validator-{idx}"
        port = start_port + idx
        created.append(create_validator(name, host, port, output_dir, stake))
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a validator config")
    parser.add_argument("--name", help="Single validator name")
    parser.add_argument("--count", type=int, default=0, help="Number of deterministic validators to generate")
    parser.add_argument("--host", default="127.0.0.1", help="Validator host")
    parser.add_argument("--port", type=int, default=9100, help="Single validator port")
    parser.add_argument("--start-port", type=int, default=9000, help="Starting port for --count generation")
    parser.add_argument("--stake", type=int, default=1000, help="Validator stake amount")
    parser.add_argument(
        "--output-dir",
        default="testnet/validators",
        help="Directory for validator configs",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if args.count > 0:
        created = create_validator_registry(args.count, args.host, args.start_port, args.stake, output_dir)
        print(f"Created validator configs: {len(created)}")
        return

    if not args.name:
        raise SystemExit("--name is required when --count is not provided")

    path = create_validator(args.name, args.host, args.port, output_dir, args.stake)
    print(f"Created validator config: {path}")


if __name__ == "__main__":
    main()
