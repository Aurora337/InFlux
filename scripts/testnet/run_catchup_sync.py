#!/usr/bin/env python3
"""Run v0.8.2 catch-up synchronization scenario for an offline validator."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def run_catchup(validators: int, epoch: int, target_validator: str, blocks_missed: int, ledger_height: int) -> None:
    _run([sys.executable, "launch_testnet.py", "--validators", str(validators), "--epoch", str(epoch)])
    _run(
        [
            sys.executable,
            "scripts/testnet/exchange_state.py",
            "--ledger-height",
            str(ledger_height),
            "--exclude-validator",
            target_validator,
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/testnet/verify_state_sync.py",
            "--target-validator",
            target_validator,
            "--blocks-missed",
            str(blocks_missed),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic catch-up synchronization scenario")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument("--target-validator", default="validator-5", help="Offline validator to recover")
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    args = parser.parse_args()

    run_catchup(
        validators=args.validators,
        epoch=args.epoch,
        target_validator=args.target_validator,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
    )

    print("Catch-up synchronization scenario complete")


if __name__ == "__main__":
    main()
