#!/usr/bin/env python3
"""Run v0.8.5 partial replay stress simulation with deterministic timeout/retry metrics."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _build_replay_plan(blocks_missed: int, chunk_size: int, timeout_every: int, retry_budget: int) -> tuple[list[dict], int, int, bool]:
    total_chunks = max(math.ceil(blocks_missed / chunk_size), 1)
    retries_remaining = retry_budget
    replayed_total = 0
    timeout_events = 0
    retry_exhausted = False
    plan: list[dict] = []

    for chunk_index in range(1, total_chunks + 1):
        blocks_this_chunk = min(chunk_size, blocks_missed - replayed_total)
        if blocks_this_chunk <= 0:
            break

        timeout_triggered = timeout_every > 0 and chunk_index % timeout_every == 0
        retry_used = 0

        if timeout_triggered:
            timeout_events += 1
            if retries_remaining > 0:
                retry_used = 1
                retries_remaining -= 1
            else:
                retry_exhausted = True

        if retry_exhausted:
            break

        replayed_total += blocks_this_chunk
        plan.append(
            {
                "chunk_index": chunk_index,
                "blocks_replayed": blocks_this_chunk,
                "timeout_triggered": timeout_triggered,
                "retry_used": retry_used,
                "replayed_total": replayed_total,
            }
        )

    return plan, timeout_events, retry_budget - retries_remaining, retry_exhausted


def render_markdown(report: dict) -> str:
    lines = [
        "# v0.8.5 Partial Replay Stress Report",
        "",
        f"- Target Validator: {report['target_validator']}",
        f"- Blocks Missed: {report['blocks_missed']}",
        f"- Chunk Size: {report['chunk_size']}",
        f"- Timeout Every N Chunks: {report['timeout_every']}",
        f"- Retry Budget: {report['retry_budget']}",
        f"- Retry Used: {report['retry_used']}",
        f"- Timeout Events: {report['timeout_events']}",
        f"- Replay Chunks Completed: {report['replay_chunks_completed']}",
        f"- Replay Chunks Expected: {report['replay_chunks_expected']}",
        f"- Blocks Replayed: {report['blocks_replayed']}",
        f"- Retry Exhausted: {report['retry_exhausted']}",
        f"- Failure Reason: {report['failure_reason']}",
        f"- Final Hash Match: {report['final_hash_match']}",
        f"- Base Recovery Success: {report['base_recovery_success']}",
        f"- Stress Success: {report['stress_success']}",
        f"- Recovery Time Seconds: {report['recovery_time_seconds']}",
        "",
        "## Replay Plan",
        "",
    ]

    for entry in report["replay_plan"]:
        lines.append(
            f"- chunk={entry['chunk_index']} blocks={entry['blocks_replayed']} timeout={entry['timeout_triggered']} retry_used={entry['retry_used']} replayed_total={entry['replayed_total']}"
        )

    return "\n".join(lines) + "\n"


def run_stress(
    validators: int,
    epoch: int,
    target_validator: str,
    blocks_missed: int,
    chunk_size: int,
    timeout_every: int,
    retry_budget: int,
    ledger_height: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    _run([sys.executable, "launch_testnet.py", "--validators", str(validators), "--epoch", str(epoch)])
    _run(
        [
            sys.executable,
            "scripts/testnet/exchange_state.py",
            "--ledger-height",
            str(ledger_height),
            "--exclude-validator",
            target_validator,
        ]
    )

    base_json = output_json.parent / "sync_report_v085_base.json"
    base_md = output_md.parent / "sync_report_v085_base.md"
    _run(
        [
            sys.executable,
            "scripts/testnet/verify_state_sync.py",
            "--target-validator",
            target_validator,
            "--blocks-missed",
            str(blocks_missed),
            "--output-json",
            str(base_json),
            "--output-md",
            str(base_md),
        ]
    )

    base_report = json.loads(base_json.read_text(encoding="utf-8"))

    replay_plan, timeout_events, retry_used, retry_exhausted = _build_replay_plan(
        blocks_missed=blocks_missed,
        chunk_size=chunk_size,
        timeout_every=timeout_every,
        retry_budget=retry_budget,
    )

    replay_chunks_expected = max(math.ceil(blocks_missed / chunk_size), 1)
    blocks_replayed = replay_plan[-1]["replayed_total"] if replay_plan else 0

    stress_success = (
        base_report.get("recovery_success", False)
        and base_report.get("final_hash_match", False)
        and blocks_replayed == blocks_missed
        and not retry_exhausted
    )

    failure_reason = "none"
    if not stress_success:
        if not base_report.get("recovery_success", False):
            failure_reason = "base_recovery_failed"
        elif not base_report.get("final_hash_match", False):
            failure_reason = "final_hash_mismatch"
        elif retry_exhausted:
            failure_reason = "retry_exhausted"
        elif blocks_replayed != blocks_missed:
            failure_reason = "incomplete_replay"
        else:
            failure_reason = "unknown"

    # Deterministic timing model: base sync + timeout penalties + retry overhead.
    recovery_time_seconds = round(
        float(base_report.get("recovery_time_seconds", 0.0)) + (timeout_events * 0.35) + (retry_used * 0.08),
        3,
    )

    report = {
        "suite": "v0.8.5-partial-replay-stress",
        "target_validator": target_validator,
        "blocks_missed": blocks_missed,
        "chunk_size": chunk_size,
        "timeout_every": timeout_every,
        "retry_budget": retry_budget,
        "retry_used": retry_used,
        "timeout_events": timeout_events,
        "replay_chunks_completed": len(replay_plan),
        "replay_chunks_expected": replay_chunks_expected,
        "replay_plan": replay_plan,
        "blocks_replayed": blocks_replayed,
        "retry_exhausted": retry_exhausted,
        "failure_reason": failure_reason,
        "final_hash_match": bool(base_report.get("final_hash_match", False)),
        "base_recovery_success": bool(base_report.get("recovery_success", False)),
        "stress_success": stress_success,
        "recovery_time_seconds": recovery_time_seconds,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(report), encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic partial replay stress simulation")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument("--target-validator", default="validator-5", help="Offline validator to recover")
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--chunk-size", type=int, default=20, help="Replay chunk size")
    parser.add_argument("--timeout-every", type=int, default=3, help="Trigger a timeout every N chunks")
    parser.add_argument("--retry-budget", type=int, default=3, help="Deterministic retry budget")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/partial_replay_report.json",
        help="Output JSON report",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/partial_replay_report.md",
        help="Output markdown report",
    )
    args = parser.parse_args()

    if args.chunk_size <= 0:
        raise SystemExit("--chunk-size must be > 0")
    if args.blocks_missed <= 0:
        raise SystemExit("--blocks-missed must be > 0")

    report = run_stress(
        validators=args.validators,
        epoch=args.epoch,
        target_validator=args.target_validator,
        blocks_missed=args.blocks_missed,
        chunk_size=args.chunk_size,
        timeout_every=args.timeout_every,
        retry_budget=args.retry_budget,
        ledger_height=args.ledger_height,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Stress success: {report['stress_success']}")
    print(f"Timeout events: {report['timeout_events']}")
    print(f"Retry used: {report['retry_used']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0 if report["stress_success"] else 1)


if __name__ == "__main__":
    main()
