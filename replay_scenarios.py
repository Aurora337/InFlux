#!/usr/bin/env python3
"""Run replay audit across all scenario JSON files and aggregate determinism stats."""

import argparse
import json
import sys

sys.path.insert(0, "harness/replay-engine")

from replay_scenario_runner import run_all_scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description="InFlux scenario replay batch")
    parser.add_argument("--scenarios-dir", default="scenarios", help="Scenario JSON directory")
    parser.add_argument("--output-root", default="data/replays", help="Replay output root")
    parser.add_argument("--verbose", action="store_true", help="Include per-scenario details")
    args = parser.parse_args()

    payload = run_all_scenarios(scenarios_dir=args.scenarios_dir, output_root=args.output_root)

    if not args.verbose:
        payload = {
            "scenarios_checked": payload["scenarios_checked"],
            "scenarios_passed": payload["scenarios_passed"],
            "scenarios_failed": payload["scenarios_failed"],
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
