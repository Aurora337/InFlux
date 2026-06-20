#!/usr/bin/env python3
"""Run economic verification scenarios and emit reports for v0.6 evidence."""

import argparse
import json
import sys

sys.path.insert(0, "harness/economic-stress")

from economic_verification_engine import run_economic_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="InFlux economic verification harness")
    parser.add_argument("--scenarios-dir", default="scenarios/economic", help="Economic scenario directory")
    parser.add_argument("--report-dir", default="reports/economic", help="Output report directory")
    parser.add_argument("--output", help="Optional aggregate output JSON path")
    args = parser.parse_args()

    payload = run_economic_suite(scenarios_dir=args.scenarios_dir, report_dir=args.report_dir)

    print(json.dumps(payload, indent=2))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    return 0 if payload["ledger_integrity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
