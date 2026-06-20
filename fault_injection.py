#!/usr/bin/env python3
"""Run adversarial/fault scenarios and report resilience metrics."""

import argparse
import json
import sys

sys.path.insert(0, "harness/node-mesh-sim")

from fault_injection_harness import run_fault_injection_scenario, run_fault_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="InFlux fault injection harness")
    parser.add_argument("--scenario", help="Single scenario JSON path")
    parser.add_argument("--scenarios-dir", default="scenarios/fault", help="Scenario directory")
    parser.add_argument("--verbose", action="store_true", help="Include detailed round traces")
    args = parser.parse_args()

    if args.scenario:
        payload = run_fault_injection_scenario(args.scenario)
    else:
        payload = run_fault_suite(args.scenarios_dir)

    if not args.verbose:
        if "results" in payload and payload.get("scenario") is None:
            payload = {
                "scenarios_checked": payload["scenarios_checked"],
                "scenarios_passed": payload["scenarios_passed"],
                "scenarios_failed": payload["scenarios_failed"],
                "agreement_rate": payload["agreement_rate"],
                "recovery_rate": payload["recovery_rate"],
                "replay_success_rate": payload["replay_success_rate"],
            }
        else:
            payload = {
                "scenario": payload["scenario"],
                "validators": payload["validators"],
                "rounds_checked": payload["rounds_checked"],
                "rounds_passed": payload["rounds_passed"],
                "rounds_failed": payload["rounds_failed"],
                "agreement_rate": payload["agreement_rate"],
                "recovery_rate": payload["recovery_rate"],
                "replay_success_rate": payload["replay_success_rate"],
                "divergence_count": payload["divergence_count"],
                "final_state_hash": payload["final_state_hash"],
            }

    print(json.dumps(payload, indent=2))

    if args.scenario:
        return 0 if payload.get("rounds_failed", 1) == 0 else 1
    return 0 if payload.get("scenarios_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
