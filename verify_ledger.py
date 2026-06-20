#!/usr/bin/env python3
"""Verify ledger integrity by replaying deterministic transitions from genesis."""

import argparse
import json
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "harness/replay-engine")

from kernel.state import State
from replay_audit import audit_ledger_replay


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify InFlux ledger replay determinism")
    parser.add_argument("--data-dir", default="data/blocks", help="Path to block storage")
    parser.add_argument("--epoch", type=int, default=0, help="Genesis epoch")
    parser.add_argument("--supply", type=float, default=1000.0, help="Genesis supply")
    parser.add_argument("--participants", type=int, default=100, help="Genesis participants")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    initial_state = State(
        epoch=args.epoch,
        supply=args.supply,
        participants=args.participants,
    )

    report = audit_ledger_replay(initial_state=initial_state, data_dir=args.data_dir)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print("LEDGER REPLAY VERIFICATION")
        print("=" * 40)
        print(f"Chain Integrity: {report.ledger_integrity}")

        if report.blocks_checked == 0:
            print("No blocks found in ledger.")
        else:
            for item in report.details:
                print(f"\nBlock Height: {item.block_height}")
                print(f"Stored Hash: {item.stored_hash}")
                print(f"Replay Hash: {item.replay_hash}")
                print(f"State Hash: {'Verified' if item.passed else 'FAILED'}")
                print(f"Status: {'PASS' if item.passed else 'FAIL'}")

        print("\nSUMMARY")
        print("-" * 40)
        print(f"Blocks Checked: {report.blocks_checked}")
        print(f"Blocks Passed: {report.blocks_passed}")
        print(f"Blocks Failed: {report.blocks_failed}")
        print(f"Replay Success Rate: {report.replay_success_rate:.4f}")
        print(f"Determinism Score: {report.determinism_score:.4f}")

    if report.ledger_integrity == "PASS":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
