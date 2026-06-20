#!/usr/bin/env python3
"""Run v0.8.5 matrix replay stress scenarios across targets and retry profiles."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _parse_profiles(profile_values: list[str]) -> list[tuple[int, int, int]]:
    profiles: list[tuple[int, int, int]] = []
    for value in profile_values:
        parts = value.split(":")
        if len(parts) != 3:
            raise SystemExit(f"Invalid profile format: {value}. Expected chunk:timeout:retry")
        chunk_size, timeout_every, retry_budget = (int(parts[0]), int(parts[1]), int(parts[2]))
        if chunk_size <= 0:
            raise SystemExit(f"Invalid profile {value}: chunk_size must be > 0")
        if timeout_every < 0:
            raise SystemExit(f"Invalid profile {value}: timeout_every must be >= 0")
        if retry_budget < 0:
            raise SystemExit(f"Invalid profile {value}: retry_budget must be >= 0")
        profiles.append((chunk_size, timeout_every, retry_budget))
    return profiles


def run_matrix(
    validators: int,
    epoch: int,
    targets: list[str],
    profiles: list[tuple[int, int, int]],
    blocks_missed: int,
    ledger_height: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    scenarios: list[dict] = []

    for target in targets:
        for chunk_size, timeout_every, retry_budget in profiles:
            profile_name = f"c{chunk_size}_t{timeout_every}_r{retry_budget}"
            scenario_id = f"{target}_{profile_name}"
            scenario_json = output_json.parent / f"partial_replay_{scenario_id}.json"
            scenario_md = output_md.parent / f"partial_replay_{scenario_id}.md"

            _run(
                [
                    sys.executable,
                    "scripts/testnet/run_partial_replay_stress.py",
                    "--validators",
                    str(validators),
                    "--epoch",
                    str(epoch),
                    "--target-validator",
                    target,
                    "--blocks-missed",
                    str(blocks_missed),
                    "--chunk-size",
                    str(chunk_size),
                    "--timeout-every",
                    str(timeout_every),
                    "--retry-budget",
                    str(retry_budget),
                    "--ledger-height",
                    str(ledger_height),
                    "--output-json",
                    str(scenario_json),
                    "--output-md",
                    str(scenario_md),
                ]
            )

            report = json.loads(scenario_json.read_text(encoding="utf-8"))
            report["scenario_id"] = scenario_id
            report["profile"] = {
                "chunk_size": chunk_size,
                "timeout_every": timeout_every,
                "retry_budget": retry_budget,
            }
            scenarios.append(report)

    scenario_count = len(scenarios)
    success_count = sum(1 for scenario in scenarios if scenario.get("stress_success"))
    total_timeout_events = sum(int(scenario.get("timeout_events", 0)) for scenario in scenarios)
    total_retry_used = sum(int(scenario.get("retry_used", 0)) for scenario in scenarios)
    avg_recovery_time = round(
        sum(float(scenario.get("recovery_time_seconds", 0.0)) for scenario in scenarios) / scenario_count,
        3,
    ) if scenario_count else 0.0

    suite = {
        "suite": "v0.8.5-partial-replay-matrix",
        "targets": targets,
        "profiles": [
            {"chunk_size": item[0], "timeout_every": item[1], "retry_budget": item[2]} for item in profiles
        ],
        "blocks_missed": blocks_missed,
        "scenarios": scenario_count,
        "successes": success_count,
        "all_successful": success_count == scenario_count,
        "total_timeout_events": total_timeout_events,
        "total_retry_used": total_retry_used,
        "average_recovery_time_seconds": avg_recovery_time,
        "scenario_reports": scenarios,
    }

    output_json.write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.5 Partial Replay Matrix Report",
        "",
        f"- Targets: {', '.join(targets)}",
        f"- Profiles: {len(profiles)}",
        f"- Blocks Missed: {blocks_missed}",
        f"- Scenarios: {suite['scenarios']}",
        f"- Successes: {suite['successes']}",
        f"- All Successful: {suite['all_successful']}",
        f"- Total Timeout Events: {suite['total_timeout_events']}",
        f"- Total Retry Used: {suite['total_retry_used']}",
        f"- Average Recovery Time Seconds: {suite['average_recovery_time_seconds']}",
        "",
        "## Scenario Results",
        "",
    ]

    for scenario in scenarios:
        lines.append(
            f"- {scenario['scenario_id']}: target={scenario['target_validator']} stress_success={scenario['stress_success']} timeout_events={scenario['timeout_events']} retry_used={scenario['retry_used']} recovery_time_seconds={scenario['recovery_time_seconds']}"
        )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic partial replay matrix")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument(
        "--targets",
        nargs="+",
        default=["validator-3", "validator-4", "validator-5"],
        help="Offline validators to evaluate",
    )
    parser.add_argument(
        "--profiles",
        nargs="+",
        default=["20:3:3", "25:2:2", "10:5:2"],
        help="Replay profiles in chunk:timeout:retry format",
    )
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/partial_replay_matrix_report.json",
        help="Consolidated matrix JSON report",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/partial_replay_matrix_report.md",
        help="Consolidated matrix markdown report",
    )
    args = parser.parse_args()

    if args.blocks_missed <= 0:
        raise SystemExit("--blocks-missed must be > 0")

    profiles = _parse_profiles(args.profiles)

    report = run_matrix(
        validators=args.validators,
        epoch=args.epoch,
        targets=args.targets,
        profiles=profiles,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Scenarios: {report['scenarios']}")
    print(f"Successes: {report['successes']}")
    print(f"All Successful: {report['all_successful']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0 if report["all_successful"] else 1)


if __name__ == "__main__":
    main()
