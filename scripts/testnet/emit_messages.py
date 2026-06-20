#!/usr/bin/env python3
"""Emit deterministic validator STATE_SYNC messages from snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _load_snapshots(snapshots_dir: Path) -> dict[str, dict]:
    snapshots: dict[str, dict] = {}
    for path in sorted(snapshots_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        validator_id = payload.get("validator_id")
        if validator_id:
            snapshots[validator_id] = payload
    return snapshots


def emit_messages(
    snapshots_dir: Path,
    output_dir: Path,
    fault_mode: str,
    fault_validator: str,
) -> list[Path]:
    snapshots = _load_snapshots(snapshots_dir)
    validators = sorted(snapshots.keys())

    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("*.json"):
        stale.unlink()

    generated: list[Path] = []

    for from_id in validators:
        sender_snapshot = snapshots[from_id]
        for to_id in validators:
            if from_id == to_id:
                continue

            if fault_mode == "drop_outbound" and fault_validator and from_id == fault_validator:
                continue

            message_hash = sender_snapshot.get("state_hash")
            fault_injected = False
            if fault_mode == "message_hash_mismatch" and fault_validator and from_id == fault_validator:
                message_hash = hashlib.sha256(f"msg-fault::{message_hash}".encode("utf-8")).hexdigest()
                fault_injected = True

            message = {
                "from": from_id,
                "to": to_id,
                "message_type": "STATE_SYNC",
                "epoch": sender_snapshot.get("epoch"),
                "state_hash": message_hash,
                "timestamp": sender_snapshot.get("timestamp"),
                "fault_injected": fault_injected,
            }
            path = output_dir / f"{from_id}_to_{to_id}.json"
            path.write_text(json.dumps(message, indent=2) + "\n", encoding="utf-8")
            generated.append(path)

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit deterministic validator STATE_SYNC messages")
    parser.add_argument(
        "--snapshots-dir",
        default="testnet/launch/snapshots",
        help="Directory containing validator snapshots",
    )
    parser.add_argument(
        "--output-dir",
        default="testnet/messages",
        help="Directory to write emitted messages",
    )
    parser.add_argument(
        "--fault-mode",
        choices=["none", "message_hash_mismatch", "drop_outbound"],
        default="none",
        help="Optional message fault injection mode",
    )
    parser.add_argument(
        "--fault-validator",
        default="",
        help="Validator id to inject message fault into",
    )
    args = parser.parse_args()

    generated = emit_messages(
        Path(args.snapshots_dir),
        Path(args.output_dir),
        args.fault_mode,
        args.fault_validator,
    )
    print(f"Emitted messages: {len(generated)}")


if __name__ == "__main__":
    main()
