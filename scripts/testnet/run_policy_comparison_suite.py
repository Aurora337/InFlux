#!/usr/bin/env python3
"""Run v0.8.6 adaptive retry policy comparison with deterministic scoring."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def _policy_score(stress_success: bool, retry_used: int, timeout_events: int, recovery_time: float) -> float:
    success_bonus = 100.0 if stress_success else 0.0
    retry_penalty = retry_used * 6.0
    timeout_penalty = timeout_events * 4.0
    latency_penalty = recovery_time * 8.0
    return round(success_bonus - retry_penalty - timeout_penalty - latency_penalty, 3)


def run_suite(
    validators: int,
    epoch: int,
    target_validator: str,
    blocks_missed: int,
    ledger_height: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    policies = [
        {
            "policy_id": "policy_linear",
            "chunk_size": 20,
            "timeout_every": 3,
            "retry_budget": 3,
            "policy_description": "Balanced linear retries",
        },
        {
            "policy_id": "policy_conservative",
            "chunk_size": 25,
            "timeout_every": 4,
            "retry_budget": 2,
            "policy_description": "Larger chunks with fewer retries",
        },
        {
            "policy_id": "policy_aggressive",
            "chunk_size": 10,
            "timeout_every": 2,
            "retry_budget": 5,
            "policy_description": "Aggressive replay with high retry capacity",
        },
    ]

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    policy_reports: list[dict] = []

    for policy in policies:
        scenario_json = output_json.parent / f"policy_compare_{policy['policy_id']}.json"
        scenario_md = output_md.parent / f"policy_compare_{policy['policy_id']}.md"

        command = [
            sys.executable,
            "scripts/testnet/run_partial_replay_stress.py",
            "--validators",
            str(validators),
            "--epoch",
            str(epoch),
            "--target-validator",
            target_validator,
            "--blocks-missed",
            str(blocks_missed),
            "--chunk-size",
            str(policy["chunk_size"]),
            "--timeout-every",
            str(policy["timeout_every"]),
            "--retry-budget",
            str(policy["retry_budget"]),
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
                f"Policy scenario {policy['policy_id']} did not emit report. Exit={completed.returncode}\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

        report = json.loads(scenario_json.read_text(encoding="utf-8"))
        stress_success = bool(report.get("stress_success", False))
        retry_used = int(report.get("retry_used", 0))
        timeout_events = int(report.get("timeout_events", 0))
        recovery_time = float(report.get("recovery_time_seconds", 0.0))

        scored = {
            "policy_id": policy["policy_id"],
            "policy_description": policy["policy_description"],
            "chunk_size": policy["chunk_size"],
            "timeout_every": policy["timeout_every"],
            "retry_budget": policy["retry_budget"],
            "observed_exit": completed.returncode,
            "stress_success": stress_success,
            "failure_reason": report.get("failure_reason", "none"),
            "retry_used": retry_used,
            "timeout_events": timeout_events,
            "recovery_time_seconds": recovery_time,
            "score": _policy_score(stress_success, retry_used, timeout_events, recovery_time),
        }
        policy_reports.append(scored)

    ranked = sorted(
        policy_reports,
        key=lambda item: (item["score"], item["stress_success"], -item["recovery_time_seconds"]),
        reverse=True,
    )
    winner = ranked[0] if ranked else None

    suite = {
        "suite": "v0.8.6-policy-comparison-suite",
        "target_validator": target_validator,
        "blocks_missed": blocks_missed,
        "policies_evaluated": len(policy_reports),
        "winner": winner,
        "ranked_policies": ranked,
    }

    output_json.write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.6 Policy Comparison Suite Report",
        "",
        f"- Target Validator: {suite['target_validator']}",
        f"- Blocks Missed: {suite['blocks_missed']}",
        f"- Policies Evaluated: {suite['policies_evaluated']}",
        f"- Winner: {winner['policy_id'] if winner else 'none'}",
        "",
        "## Ranked Policies",
        "",
    ]

    for item in ranked:
        lines.append(
            f"- {item['policy_id']}: score={item['score']} stress_success={item['stress_success']} retry_used={item['retry_used']} timeout_events={item['timeout_events']} recovery_time_seconds={item['recovery_time_seconds']}"
        )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic adaptive retry policy comparison suite")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument("--target-validator", default="validator-5", help="Offline validator target")
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/policy_comparison_suite.json",
        help="Suite JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/policy_comparison_suite.md",
        help="Suite markdown output path",
    )
    args = parser.parse_args()

    suite = run_suite(
        validators=args.validators,
        epoch=args.epoch,
        target_validator=args.target_validator,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    winner_id = suite["winner"]["policy_id"] if suite.get("winner") else "none"
    print(f"Policies Evaluated: {suite['policies_evaluated']}")
    print(f"Winner: {winner_id}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    if not suite.get("winner"):
        raise SystemExit(1)

    raise SystemExit(0)


if __name__ == "__main__":
    main()
