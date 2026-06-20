#!/usr/bin/env python3
"""One-command local testnet bootstrap simulation for v0.7 scaffolding."""

from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="Launch deterministic local testnet workflow")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators to launch")
    parser.add_argument("--epoch", type=int, default=1, help="Snapshot epoch")
    parser.add_argument(
        "--fault-mode",
        choices=["none", "snapshot_hash_mismatch", "message_hash_mismatch", "drop_outbound"],
        default="none",
        help="Optional deterministic fault injection mode",
    )
    parser.add_argument(
        "--fault-validator",
        default="",
        help="Validator id to inject fault into (e.g. validator-3)",
    )
    args = parser.parse_args()

    validator_count = args.validators

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
            str(args.epoch),
            "--fault-mode",
            args.fault_mode if args.fault_mode == "snapshot_hash_mismatch" else "none",
            "--fault-validator",
            args.fault_validator,
        ]
    )

    run_step(
        [
            sys.executable,
            "scripts/testnet/emit_messages.py",
            "--fault-mode",
            args.fault_mode if args.fault_mode in {"message_hash_mismatch", "drop_outbound"} else "none",
            "--fault-validator",
            args.fault_validator,
        ]
    )
    print("Validator Handshake Complete")

    run_step(
        [
            sys.executable,
            "scripts/testnet/verify_network.py",
            "--expected-validators",
            str(validator_count),
            "--epoch",
            str(args.epoch),
            "--allow-unhealthy",
        ]
    )

    health_path = ROOT / "testnet/launch/network_health.json"
    consensus_status = "degraded"
    network_status = "unhealthy"
    if health_path.exists():
        health_payload = json.loads(health_path.read_text(encoding="utf-8"))
        consensus_status = str(health_payload.get("consensus_status", "degraded"))
        network_status = str(health_payload.get("network_status", "unhealthy"))

    if consensus_status == "established":
        print("Consensus Established")
    else:
        print("Consensus Degraded")

    if network_status == "healthy":
        print("Network Healthy")
    else:
        print("Network Unhealthy")


if __name__ == "__main__":
    main()
