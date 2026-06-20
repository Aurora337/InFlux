#!/usr/bin/env python3
"""Create deterministic state payloads from validator snapshots for sync testing."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _canonical_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def exchange_state(
    snapshots_dir: Path,
    output_dir: Path,
    ledger_height: int,
    exclude_validator: str,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("*.json"):
        stale.unlink()

    generated: list[Path] = []
    for snapshot_path in sorted(snapshots_dir.glob("*.json")):
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        validator_id = snapshot["validator_id"]
        if exclude_validator and validator_id == exclude_validator:
            continue
        epoch = int(snapshot["epoch"])

        state_payload = {
            "validator_id": validator_id,
            "epoch": epoch,
            "state_hash": snapshot["state_hash"],
            "ledger_height": ledger_height,
            "timestamp": snapshot["timestamp"],
        }
        state_payload["payload_hash"] = _canonical_hash(state_payload)

        out_path = output_dir / f"{validator_id}.json"
        out_path.write_text(json.dumps(state_payload, indent=2) + "\n", encoding="utf-8")
        generated.append(out_path)

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic state payloads from snapshots")
    parser.add_argument("--snapshots-dir", default="testnet/launch/snapshots", help="Input snapshot directory")
    parser.add_argument("--output-dir", default="testnet/state", help="Output state payload directory")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Deterministic ledger height value")
    parser.add_argument(
        "--exclude-validator",
        default="",
        help="Optional validator id to omit from exchanged state payloads",
    )
    args = parser.parse_args()

    generated = exchange_state(
        Path(args.snapshots_dir),
        Path(args.output_dir),
        args.ledger_height,
        args.exclude_validator,
    )
    print(f"State payloads generated: {len(generated)}")


if __name__ == "__main__":
    main()
