#!/usr/bin/env python3
"""Emit deterministic validator STATE_SYNC messages from snapshots."""

from __future__ import annotations

import argparse
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


def emit_messages(snapshots_dir: Path, output_dir: Path) -> list[Path]:
    snapshots = _load_snapshots(snapshots_dir)
    validators = sorted(snapshots.keys())

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    for from_id in validators:
        sender_snapshot = snapshots[from_id]
        for to_id in validators:
            if from_id == to_id:
                continue
            message = {
                "from": from_id,
                "to": to_id,
                "message_type": "STATE_SYNC",
                "epoch": sender_snapshot.get("epoch"),
                "state_hash": sender_snapshot.get("state_hash"),
                "timestamp": sender_snapshot.get("timestamp"),
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
    args = parser.parse_args()

    generated = emit_messages(Path(args.snapshots_dir), Path(args.output_dir))
    print(f"Emitted messages: {len(generated)}")


if __name__ == "__main__":
    main()
