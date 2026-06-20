#!/usr/bin/env python3
"""One-command local testnet bootstrap simulation for v0.7 scaffolding."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_step(args: list[str]) -> None:
    completed = subprocess.run(args, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    validator_count = 5

    run_step([sys.executable, "scripts/testnet/generate_genesis.py", "--validators", str(validator_count)])

    for idx in range(1, validator_count + 1):
        name = f"Validator-{idx}"
        port = 9100 + idx
        run_step(
            [
                sys.executable,
                "scripts/testnet/create_validator.py",
                "--name",
                name,
                "--port",
                str(port),
            ]
        )
        run_step(
            [
                sys.executable,
                "scripts/testnet/launch_validator.py",
                "--config",
                f"testnet/validators/{name}.json",
            ]
        )

    run_step([sys.executable, "scripts/testnet/bootstrap_network.py"])
    run_step([sys.executable, "scripts/testnet/verify_network.py", "--expected-validators", str(validator_count)])

    print("Consensus Established")
    print("Network Healthy")


if __name__ == "__main__":
    main()
