#!/usr/bin/env python3
"""Run full replay audit from genesis and emit deterministic health evidence."""

import argparse
import json
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "harness/replay-engine")

from influx.kernel.state import State
from replay_audit import audit_ledger_replay


def main() -> int:
    parser = argparse.ArgumentParser(description="InFlux replay audit")
    parser.add_argument("--data-dir", default="data/blocks", help="Path to block storage")
    parser.add_argument("--epoch", type=int, default=0, help="Genesis epoch")
    parser.add_argument("--supply", type=float, default=1000.0, help="Genesis supply")
    parser.add_argument("--participants", type=int, default=100, help="Genesis participants")
    parser.add_argument("--verbose", action="store_true", help="Include per-block details")
    args = parser.parse_args()

    initial_state = State(
        epoch=args.epoch,
        supply=args.supply,
        participants=args.participants,
    )

    report = audit_ledger_replay(initial_state=initial_state, data_dir=args.data_dir)
    payload = report.to_dict()

    if not args.verbose:
        payload = {
            "genesis_hash": payload["genesis_hash"],
            "blocks_checked": payload["blocks_checked"],
            "blocks_passed": payload["blocks_passed"],
            "blocks_failed": payload["blocks_failed"],
            "replay_success_rate": payload["replay_success_rate"],
            "determinism_score": payload["determinism_score"],
            "ledger_integrity": payload["ledger_integrity"],
        }

    print(json.dumps(payload, indent=2))

    return 0 if payload["ledger_integrity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
