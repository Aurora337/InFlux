#!/usr/bin/env python3
"""Generate a deterministic evidence report for the current environment."""

import argparse
import json
import os
import sys

sys.path.insert(0, "harness/replay-engine")

from environment_report import build_environment_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate cross-environment determinism report")
    parser.add_argument("--environment", required=True, help="Environment label, e.g. Linux, Windows, Docker, CI")
    parser.add_argument("--replay-data-dir", default="data/blocks_demo_verify", help="Ledger directory for replay audit")
    parser.add_argument("--scenarios-dir", default="scenarios", help="Scenario directory")
    parser.add_argument("--scenario-output-root", default="data/replays", help="Scenario replay output root")
    parser.add_argument("--consensus-rounds", type=int, default=25, help="Consensus rounds for hash report")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    report = build_environment_report(
        environment=args.environment,
        replay_data_dir=args.replay_data_dir,
        scenarios_dir=args.scenarios_dir,
        scenario_output_root=args.scenario_output_root,
        consensus_rounds=args.consensus_rounds,
    )

    payload = report.to_dict()
    print(json.dumps(payload, indent=2))

    output = args.output
    if not output:
        output = f"data/replays/reports/{args.environment.lower()}_report.json"

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return 0 if payload["ledger_integrity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
