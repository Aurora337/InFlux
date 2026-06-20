#!/usr/bin/env python3
"""Run v0.8.3 staggered catch-up synchronization across multiple offline validators."""

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


def run_staggered(
    validators: int,
    epoch: int,
    targets: list[str],
    blocks_missed: int,
    ledger_height: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    _run([sys.executable, "launch_testnet.py", "--validators", str(validators), "--epoch", str(epoch)])

    target_reports: list[dict] = []
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    for target in targets:
        _run(
            [
                sys.executable,
                "scripts/testnet/exchange_state.py",
                "--ledger-height",
                str(ledger_height),
                "--exclude-validator",
                target,
            ]
        )

        target_json = output_json.parent / f"sync_report_{target}.json"
        target_md = output_md.parent / f"sync_report_{target}.md"

        _run(
            [
                sys.executable,
                "scripts/testnet/verify_state_sync.py",
                "--target-validator",
                target,
                "--blocks-missed",
                str(blocks_missed),
                "--output-json",
                str(target_json),
                "--output-md",
                str(target_md),
            ]
        )

        report = json.loads(target_json.read_text(encoding="utf-8"))
        target_reports.append(report)

    success_count = sum(1 for report in target_reports if report.get("recovery_success"))
    suite_report = {
        "suite": "v0.8.3-staggered-catchup",
        "validators": validators,
        "epoch": epoch,
        "targets": targets,
        "scenarios": len(target_reports),
        "recoveries_successful": success_count,
        "all_recoveries_successful": success_count == len(target_reports),
        "reports": target_reports,
    }

    output_json.write_text(json.dumps(suite_report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.3 Staggered Catch-Up Report",
        "",
        f"- Validators: {validators}",
        f"- Epoch: {epoch}",
        f"- Scenarios: {suite_report['scenarios']}",
        f"- Recoveries Successful: {suite_report['recoveries_successful']}",
        f"- All Recoveries Successful: {suite_report['all_recoveries_successful']}",
        "",
        "## Scenario Results",
        "",
    ]

    for report in target_reports:
        lines.append(
            f"- {report['target_validator']}: mode={report['sync_mode']} observed={report['validators_observed']}/{report['validators_expected']} final_hash_match={report['final_hash_match']} recovery_success={report['recovery_success']}"
        )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return suite_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic staggered catch-up scenarios")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument(
        "--targets",
        nargs="+",
        default=["validator-3", "validator-4", "validator-5"],
        help="Offline validators to replay one-by-one",
    )
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/staggered_sync_report.json",
        help="Consolidated JSON report",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/staggered_sync_report.md",
        help="Consolidated markdown report",
    )
    args = parser.parse_args()

    report = run_staggered(
        validators=args.validators,
        epoch=args.epoch,
        targets=args.targets,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Scenarios: {report['scenarios']}")
    print(f"Recoveries Successful: {report['recoveries_successful']}")
    print(f"All Recoveries Successful: {report['all_recoveries_successful']}")

    raise SystemExit(0 if report["all_recoveries_successful"] else 1)


if __name__ == "__main__":
    main()
