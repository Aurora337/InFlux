#!/usr/bin/env python3
"""Run v0.8.7 orchestration supervisor with retry and escalation reporting."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def run_supervisor(
    validators: int,
    epoch: int,
    blocks_missed: int,
    ledger_height: int,
    max_attempts: int,
    inject_failure_suite: str,
    inject_failure_attempt: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    attempts: list[dict] = []
    recovered = False
    escalated = False

    for attempt in range(1, max_attempts + 1):
        attempt_json = output_json.parent / f"sync_orchestration_attempt_{attempt}.json"
        attempt_md = output_md.parent / f"sync_orchestration_attempt_{attempt}.md"

        command = [
            sys.executable,
            "scripts/testnet/run_sync_orchestration.py",
            "--validators",
            str(validators),
            "--epoch",
            str(epoch),
            "--blocks-missed",
            str(blocks_missed),
            "--ledger-height",
            str(ledger_height),
            "--attempt",
            str(attempt),
            "--output-json",
            str(attempt_json),
            "--output-md",
            str(attempt_md),
        ]

        if inject_failure_suite and inject_failure_attempt > 0:
            command.extend(["--inject-failure-suite", inject_failure_suite])
            command.extend(["--inject-failure-attempt", str(inject_failure_attempt)])

        completed = _run(command)
        if not attempt_json.exists():
            raise SystemExit(
                f"Attempt {attempt} did not generate report. Exit={completed.returncode}\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

        report = json.loads(attempt_json.read_text(encoding="utf-8"))
        success = bool(report.get("orchestration_success", False)) and completed.returncode == 0

        attempt_record = {
            "attempt": attempt,
            "success": success,
            "exit_code": completed.returncode,
            "suite_results": report.get("suite_results", []),
            "policy_winner": report.get("policy_winner", {}),
        }
        attempts.append(attempt_record)

        if success:
            recovered = attempt > 1
            break

    if not attempts:
        escalated = True
    else:
        escalated = not attempts[-1]["success"]

    report = {
        "suite": "v0.8.7-sync-orchestration-supervisor",
        "max_attempts": max_attempts,
        "attempts_executed": len(attempts),
        "inject_failure_suite": inject_failure_suite,
        "inject_failure_attempt": inject_failure_attempt,
        "supervisor_success": not escalated,
        "recovered_after_retry": recovered,
        "escalated": escalated,
        "attempts": attempts,
    }

    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.7 Sync Orchestration Supervisor Report",
        "",
        f"- Max Attempts: {report['max_attempts']}",
        f"- Attempts Executed: {report['attempts_executed']}",
        f"- Inject Failure Suite: {report['inject_failure_suite'] or 'none'}",
        f"- Inject Failure Attempt: {report['inject_failure_attempt']}",
        f"- Supervisor Success: {report['supervisor_success']}",
        f"- Recovered After Retry: {report['recovered_after_retry']}",
        f"- Escalated: {report['escalated']}",
        "",
        "## Attempt Results",
        "",
    ]

    for attempt in attempts:
        lines.append(
            f"- attempt={attempt['attempt']} success={attempt['success']} exit_code={attempt['exit_code']}"
        )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic orchestration supervisor")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument("--max-attempts", type=int, default=3, help="Maximum orchestration attempts")
    parser.add_argument(
        "--inject-failure-suite",
        default="",
        choices=["", "retry_exhaustion_suite", "backoff_latency_suite", "policy_comparison_suite"],
        help="Optional suite id to fail on a specific attempt for deterministic retry testing",
    )
    parser.add_argument(
        "--inject-failure-attempt",
        type=int,
        default=0,
        help="Attempt number where injected failure occurs (0 disables)",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_orchestration_supervisor_report.json",
        help="Supervisor JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_orchestration_supervisor_report.md",
        help="Supervisor markdown output path",
    )
    args = parser.parse_args()

    if args.max_attempts <= 0:
        raise SystemExit("--max-attempts must be > 0")

    report = run_supervisor(
        validators=args.validators,
        epoch=args.epoch,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
        max_attempts=args.max_attempts,
        inject_failure_suite=args.inject_failure_suite,
        inject_failure_attempt=args.inject_failure_attempt,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Supervisor Success: {report['supervisor_success']}")
    print(f"Recovered After Retry: {report['recovered_after_retry']}")
    print(f"Escalated: {report['escalated']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0 if report["supervisor_success"] else 1)


if __name__ == "__main__":
    main()
