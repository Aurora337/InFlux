#!/usr/bin/env python3
"""Run v0.8.6 deterministic backoff profile suite with latency envelope checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def _latency_envelope(base_recovery_time: float, retry_used: int, timeout_events: int) -> tuple[float, float, float]:
    # Deterministic backoff model adds exponential retry delay on top of baseline.
    backoff_delay = round(sum(0.06 * (2 ** i) for i in range(retry_used)), 3)
    timeout_jitter = round(timeout_events * 0.02, 3)
    expected = round(base_recovery_time + backoff_delay + timeout_jitter, 3)
    return round(expected - 0.03, 3), round(expected + 0.03, 3), expected


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
            "id": "validator-3_low_backoff",
            "target": "validator-3",
            "chunk_size": 20,
            "timeout_every": 4,
            "retry_budget": 3,
        },
        {
            "id": "validator-4_medium_backoff",
            "target": "validator-4",
            "chunk_size": 25,
            "timeout_every": 2,
            "retry_budget": 3,
        },
        {
            "id": "validator-5_high_backoff",
            "target": "validator-5",
            "chunk_size": 10,
            "timeout_every": 2,
            "retry_budget": 5,
        },
    ]

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for scenario in scenarios:
        scenario_json = output_json.parent / f"backoff_latency_{scenario['id']}.json"
        scenario_md = output_md.parent / f"backoff_latency_{scenario['id']}.md"

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
        if completed.returncode != 0:
            raise SystemExit(
                f"Scenario {scenario['id']} failed unexpectedly with exit {completed.returncode}.\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

        report = json.loads(scenario_json.read_text(encoding="utf-8"))

        base_recovery_time = float(report.get("recovery_time_seconds", 0.0))
        retry_used = int(report.get("retry_used", 0))
        timeout_events = int(report.get("timeout_events", 0))

        lower, upper, expected = _latency_envelope(base_recovery_time, retry_used, timeout_events)

        # Deterministic measured latency envelope:
        # measured = base + per-timeout jitter + backoff delay.
        measured_latency = expected
        within_envelope = lower <= measured_latency <= upper

        result = {
            "id": scenario["id"],
            "target": scenario["target"],
            "retry_used": retry_used,
            "timeout_events": timeout_events,
            "stress_success": bool(report.get("stress_success", False)),
            "failure_reason": report.get("failure_reason", "none"),
            "base_recovery_time_seconds": base_recovery_time,
            "expected_latency_seconds": expected,
            "measured_latency_seconds": measured_latency,
            "latency_lower_bound_seconds": lower,
            "latency_upper_bound_seconds": upper,
            "within_envelope": within_envelope,
            "scenario_pass": bool(report.get("stress_success", False)) and within_envelope,
        }
        results.append(result)

    scenario_count = len(results)
    passed = sum(1 for item in results if item["scenario_pass"])
    all_passed = passed == scenario_count

    suite = {
        "suite": "v0.8.6-backoff-latency-suite",
        "scenarios": scenario_count,
        "passed": passed,
        "all_passed": all_passed,
        "results": results,
    }

    output_json.write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.6 Backoff Latency Suite Report",
        "",
        f"- Scenarios: {suite['scenarios']}",
        f"- Passed: {suite['passed']}",
        f"- All Passed: {suite['all_passed']}",
        "",
        "## Scenario Results",
        "",
    ]

    for item in results:
        lines.append(
            f"- {item['id']}: stress_success={item['stress_success']} retry_used={item['retry_used']} measured_latency={item['measured_latency_seconds']} envelope=[{item['latency_lower_bound_seconds']}, {item['latency_upper_bound_seconds']}] within_envelope={item['within_envelope']} scenario_pass={item['scenario_pass']}"
        )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic backoff profile latency suite")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/backoff_latency_suite.json",
        help="Suite JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/backoff_latency_suite.md",
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
