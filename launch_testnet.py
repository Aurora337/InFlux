#!/usr/bin/env python3
"""One-command local testnet bootstrap simulation for v0.7 scaffolding."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_step(args: list[str]) -> None:
    completed = subprocess.run(args, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    validator_count = 5

    run_step([
        sys.executable,
        "scripts/testnet/generate_genesis.py",
        "--validators",
        str(validator_count),
    ])
    print("Genesis Loaded")

    run_step(
        [
            sys.executable,
            "scripts/testnet/create_validator.py",
            "--count",
            str(validator_count),
            "--start-port",
            "9000",
            "--stake",
            "1000",
        ]
    )

    for path in sorted((ROOT / "testnet/validators").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        validator_id = payload["validator_id"]
        run_step(
            [
                sys.executable,
                "scripts/testnet/launch_validator.py",
                "--config",
                f"testnet/validators/{path.name}",
            ]
        )
        display_name = validator_id.replace("validator-", "Validator-")
        print(f"{display_name} Started")

    run_step([sys.executable, "scripts/testnet/bootstrap_network.py"])
    network_path = ROOT / "testnet/peers/peers.json"
    peer_count = 0
    if network_path.exists():
        payload = json.loads(network_path.read_text(encoding="utf-8"))
        peer_count = int(payload.get("peer_count", 0))
    print(f"Peers Discovered: {peer_count}")

    run_step(
        [
            sys.executable,
            "scripts/testnet/emit_snapshots.py",
            "--epoch",
            "1",
        ]
    )

    run_step(
        [
            sys.executable,
            "scripts/testnet/verify_network.py",
            "--expected-validators",
            str(validator_count),
            "--epoch",
            "1",
        ]
    )

    print("Consensus Established")
    print("Network Healthy")


if __name__ == "__main__":
    main()
