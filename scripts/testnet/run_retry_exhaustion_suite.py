#!/usr/bin/env python3
"""Run v0.8.6 retry exhaustion suite with expected success/failure outcomes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def run_suite(
    validators: int,
    epoch: int,
    blocks_missed: int,
    ledger_height: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    scenarios = [
        {
            "id": "validator-4_recovery_path",
            "target": "validator-4",
            "chunk_size": 20,
            "timeout_every": 3,
            "retry_budget": 3,
            "expected_success": True,
        },
        {
            "id": "validator-4_retry_exhaustion",
            "target": "validator-4",
            "chunk_size": 20,
            "timeout_every": 1,
            "retry_budget": 1,
            "expected_success": False,
            "expected_failure_reason": "retry_exhausted",
        },
        {
            "id": "validator-5_recovery_path",
            "target": "validator-5",
            "chunk_size": 25,
            "timeout_every": 2,
            "retry_budget": 2,
            "expected_success": True,
        },
        {
            "id": "validator-5_retry_exhaustion",
            "target": "validator-5",
            "chunk_size": 10,
            "timeout_every": 1,
            "retry_budget": 2,
            "expected_success": False,
            "expected_failure_reason": "retry_exhausted",
        },
    ]

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for scenario in scenarios:
        scenario_json = output_json.parent / f"retry_suite_{scenario['id']}.json"
        scenario_md = output_md.parent / f"retry_suite_{scenario['id']}.md"

        command = [
            sys.executable,
            "scripts/testnet/run_partial_replay_stress.py",
            "--validators",
            str(validators),
            "--epoch",
            str(epoch),
            "--target-validator",
            scenario["target"],
            "--blocks-missed",
            str(blocks_missed),
            "--chunk-size",
            str(scenario["chunk_size"]),
            "--timeout-every",
            str(scenario["timeout_every"]),
            "--retry-budget",
            str(scenario["retry_budget"]),
            "--ledger-height",
            str(ledger_height),
            "--output-json",
            str(scenario_json),
            "--output-md",
            str(scenario_md),
        ]

        completed = _run(command)
        if not scenario_json.exists():
            raise SystemExit(
                f"Scenario {scenario['id']} did not produce report. Exit={completed.returncode}\n{completed.stdout}\n{completed.stderr}"
            )

        report = json.loads(scenario_json.read_text(encoding="utf-8"))
        expected_exit = 0 if scenario["expected_success"] else 1

        scenario_pass = (
            completed.returncode == expected_exit
            and bool(report.get("stress_success")) == bool(scenario["expected_success"])
        )

        if not scenario["expected_success"]:
            scenario_pass = scenario_pass and bool(report.get("retry_exhausted"))
            expected_reason = scenario.get("expected_failure_reason", "")
            if expected_reason:
                scenario_pass = scenario_pass and report.get("failure_reason") == expected_reason

        result = {
            "id": scenario["id"],
            "target": scenario["target"],
            "expected_success": scenario["expected_success"],
            "observed_success": bool(report.get("stress_success")),
            "expected_exit": expected_exit,
            "observed_exit": completed.returncode,
            "failure_reason": report.get("failure_reason", "unknown"),
            "retry_exhausted": bool(report.get("retry_exhausted", False)),
            "timeout_events": int(report.get("timeout_events", 0)),
            "retry_used": int(report.get("retry_used", 0)),
            "blocks_replayed": int(report.get("blocks_replayed", 0)),
            "blocks_missed": int(report.get("blocks_missed", 0)),
            "scenario_pass": scenario_pass,
        }
        results.append(result)

    scenario_count = len(results)
    passed = sum(1 for item in results if item["scenario_pass"])
    expected_failures = sum(1 for item in results if not item["expected_success"])
    observed_failures = sum(1 for item in results if not item["observed_success"])

    suite = {
        "suite": "v0.8.6-retry-exhaustion-suite",
        "scenarios": scenario_count,
        "passed": passed,
        "all_passed": passed == scenario_count,
        "expected_failures": expected_failures,
        "observed_failures": observed_failures,
        "results": results,
    }

    output_json.write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.6 Retry Exhaustion Suite Report",
        "",
        f"- Scenarios: {suite['scenarios']}",
        f"- Passed: {suite['passed']}",
        f"- All Passed: {suite['all_passed']}",
        f"- Expected Failures: {suite['expected_failures']}",
        f"- Observed Failures: {suite['observed_failures']}",
        "",
        "## Scenario Results",
        "",
    ]

    for item in results:
        lines.append(
            f"- {item['id']}: expected_success={item['expected_success']} observed_success={item['observed_success']} expected_exit={item['expected_exit']} observed_exit={item['observed_exit']} failure_reason={item['failure_reason']} scenario_pass={item['scenario_pass']}"
        )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic retry exhaustion suite")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/retry_exhaustion_suite.json",
        help="Suite JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/retry_exhaustion_suite.md",
        help="Suite markdown output path",
    )
    args = parser.parse_args()

    suite = run_suite(
        validators=args.validators,
        epoch=args.epoch,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Scenarios: {suite['scenarios']}")
    print(f"Passed: {suite['passed']}")
    print(f"All Passed: {suite['all_passed']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0 if suite["all_passed"] else 1)


if __name__ == "__main__":
    main()
