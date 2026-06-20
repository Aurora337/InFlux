#!/usr/bin/env python3
"""Run v0.8.7 synchronization orchestration pipeline across resilience suites."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def run_orchestration(
    validators: int,
    epoch: int,
    blocks_missed: int,
    ledger_height: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    suites = [
        {
            "id": "retry_exhaustion_suite",
            "command": [
                sys.executable,
                "scripts/testnet/run_retry_exhaustion_suite.py",
                "--validators",
                str(validators),
                "--epoch",
                str(epoch),
                "--blocks-missed",
                str(blocks_missed),
                "--ledger-height",
                str(ledger_height),
            ],
            "report_path": ROOT / "testnet/launch/retry_exhaustion_suite.json",
        },
        {
            "id": "backoff_latency_suite",
            "command": [
                sys.executable,
                "scripts/testnet/run_backoff_latency_suite.py",
                "--validators",
                str(validators),
                "--epoch",
                str(epoch),
                "--blocks-missed",
                str(blocks_missed),
                "--ledger-height",
                str(ledger_height),
            ],
            "report_path": ROOT / "testnet/launch/backoff_latency_suite.json",
        },
        {
            "id": "policy_comparison_suite",
            "command": [
                sys.executable,
                "scripts/testnet/run_policy_comparison_suite.py",
                "--validators",
                str(validators),
                "--epoch",
                str(epoch),
                "--blocks-missed",
                str(blocks_missed),
                "--ledger-height",
                str(ledger_height),
            ],
            "report_path": ROOT / "testnet/launch/policy_comparison_suite.json",
        },
    ]

    suite_results: list[dict] = []

    for suite in suites:
        completed = _run(suite["command"])
        report_exists = suite["report_path"].exists()

        report_data: dict | None = None
        if report_exists:
            report_data = json.loads(suite["report_path"].read_text(encoding="utf-8"))

        if suite["id"] == "retry_exhaustion_suite":
            suite_passed = bool(report_data and report_data.get("all_passed")) and completed.returncode == 0
        elif suite["id"] == "backoff_latency_suite":
            suite_passed = bool(report_data and report_data.get("all_passed")) and completed.returncode == 0
        else:
            suite_passed = bool(report_data and report_data.get("winner")) and completed.returncode == 0

        suite_results.append(
            {
                "suite_id": suite["id"],
                "exit_code": completed.returncode,
                "report_generated": report_exists,
                "suite_passed": suite_passed,
                "report": report_data,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
            }
        )

    orchestration_success = all(item["suite_passed"] for item in suite_results)

    policy_winner = None
    policy_suite = next((item for item in suite_results if item["suite_id"] == "policy_comparison_suite"), None)
    if policy_suite and policy_suite.get("report"):
        policy_winner = policy_suite["report"].get("winner")

    retry_summary = None
    retry_suite = next((item for item in suite_results if item["suite_id"] == "retry_exhaustion_suite"), None)
    if retry_suite and retry_suite.get("report"):
        retry_summary = {
            "scenarios": retry_suite["report"].get("scenarios", 0),
            "passed": retry_suite["report"].get("passed", 0),
            "expected_failures": retry_suite["report"].get("expected_failures", 0),
            "observed_failures": retry_suite["report"].get("observed_failures", 0),
        }

    latency_summary = None
    latency_suite = next((item for item in suite_results if item["suite_id"] == "backoff_latency_suite"), None)
    if latency_suite and latency_suite.get("report"):
        latency_summary = {
            "scenarios": latency_suite["report"].get("scenarios", 0),
            "passed": latency_suite["report"].get("passed", 0),
            "all_passed": latency_suite["report"].get("all_passed", False),
        }

    report = {
        "suite": "v0.8.7-sync-orchestration",
        "validators": validators,
        "epoch": epoch,
        "blocks_missed": blocks_missed,
        "ledger_height": ledger_height,
        "orchestration_success": orchestration_success,
        "retry_summary": retry_summary,
        "latency_summary": latency_summary,
        "policy_winner": policy_winner,
        "suite_results": [
            {
                "suite_id": item["suite_id"],
                "exit_code": item["exit_code"],
                "report_generated": item["report_generated"],
                "suite_passed": item["suite_passed"],
            }
            for item in suite_results
        ],
    }

    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.7 Sync Orchestration Report",
        "",
        f"- Validators: {report['validators']}",
        f"- Epoch: {report['epoch']}",
        f"- Blocks Missed: {report['blocks_missed']}",
        f"- Ledger Height: {report['ledger_height']}",
        f"- Orchestration Success: {report['orchestration_success']}",
        "",
        "## Suites",
        "",
    ]

    for item in report["suite_results"]:
        lines.append(
            f"- {item['suite_id']}: passed={item['suite_passed']} exit_code={item['exit_code']} report_generated={item['report_generated']}"
        )

    if policy_winner:
        lines.extend(
            [
                "",
                "## Policy Winner",
                "",
                f"- policy_id: {policy_winner.get('policy_id', 'none')}",
                f"- score: {policy_winner.get('score', 0)}",
                f"- retry_used: {policy_winner.get('retry_used', 0)}",
                f"- timeout_events: {policy_winner.get('timeout_events', 0)}",
                f"- recovery_time_seconds: {policy_winner.get('recovery_time_seconds', 0.0)}",
            ]
        )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic synchronization orchestration pipeline")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_orchestration_report.json",
        help="Consolidated orchestration JSON report",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_orchestration_report.md",
        help="Consolidated orchestration markdown report",
    )
    args = parser.parse_args()

    report = run_orchestration(
        validators=args.validators,
        epoch=args.epoch,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Orchestration Success: {report['orchestration_success']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0 if report["orchestration_success"] else 1)


if __name__ == "__main__":
    main()
