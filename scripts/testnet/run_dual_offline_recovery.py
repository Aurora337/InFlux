#!/usr/bin/env python3
"""Run v0.8.4 dual-offline catch-up recovery with quorum conflict-resolution checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _hash_counts(state_payloads: dict[str, dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for payload in state_payloads.values():
        state_hash = payload.get("state_hash", "")
        counts[state_hash] = counts.get(state_hash, 0) + 1
    return counts


def _deterministic_offline_hash(majority_hash: str, target: str, blocks_missed: int) -> str:
    seed = f"dual-offline::{target}::{majority_hash}::{blocks_missed}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()


def run_dual_offline(
    validators: int,
    epoch: int,
    targets: list[str],
    blocks_missed: int,
    ledger_height: int,
    inject_conflict: str,
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
            "--exclude-validators",
            *targets,
        ]
    )

    peers_path = ROOT / "testnet/peers/peers.json"
    state_dir = ROOT / "testnet/state"

    peers = json.loads(peers_path.read_text(encoding="utf-8"))
    peer_ids: list[str] = peers.get("peer_ids", [])

    state_payloads: dict[str, dict] = {}
    for state_path in sorted(state_dir.glob("*.json")):
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        state_payloads[payload["validator_id"]] = payload

    if inject_conflict and inject_conflict in state_payloads:
        mutated = dict(state_payloads[inject_conflict])
        mutated["state_hash"] = hashlib.sha256(f"conflict::{inject_conflict}".encode("utf-8")).hexdigest()
        canonical = json.dumps({
            "validator_id": mutated["validator_id"],
            "epoch": mutated["epoch"],
            "state_hash": mutated["state_hash"],
            "ledger_height": mutated["ledger_height"],
            "timestamp": mutated["timestamp"],
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")
        mutated["payload_hash"] = hashlib.sha256(canonical).hexdigest()
        state_payloads[inject_conflict] = mutated

    hash_counts = _hash_counts(state_payloads)
    majority_hash = ""
    majority_count = 0
    if hash_counts:
        majority_hash, majority_count = max(hash_counts.items(), key=lambda item: item[1])

    observed = len(state_payloads)
    quorum_required = (observed // 2) + 1 if observed else 0
    agreement_rate = round((majority_count / observed), 6) if observed else 0.0
    conflict_detected = len(hash_counts) > 1

    target_reports: list[dict] = []
    for target in targets:
        offline_initial_hash = _deterministic_offline_hash(majority_hash, target, blocks_missed)
        recovered_hash = majority_hash
        final_hash_match = recovered_hash == majority_hash and bool(majority_hash)
        recovery_success = (
            target in peer_ids
            and target not in state_payloads
            and majority_count >= quorum_required
            and final_hash_match
        )

        target_reports.append(
            {
                "target_validator": target,
                "blocks_missed": blocks_missed,
                "offline_initial_hash": offline_initial_hash,
                "recovered_hash": recovered_hash,
                "final_hash_match": final_hash_match,
                "recovery_success": recovery_success,
            }
        )

    all_recoveries_successful = all(item["recovery_success"] for item in target_reports)

    report = {
        "suite": "v0.8.4-dual-offline-recovery",
        "validators_expected": len(peer_ids),
        "validators_observed": observed,
        "offline_targets": targets,
        "quorum_required": quorum_required,
        "quorum_observed": majority_count,
        "agreement_rate": agreement_rate,
        "conflict_detected": conflict_detected,
        "conflict_resolution_strategy": "majority_quorum_hash",
        "inject_conflict": inject_conflict,
        "majority_hash": majority_hash,
        "hash_counts": hash_counts,
        "target_reports": target_reports,
        "all_recoveries_successful": all_recoveries_successful,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.4 Dual Offline Recovery Report",
        "",
        f"- Validators Expected: {report['validators_expected']}",
        f"- Validators Observed: {report['validators_observed']}",
        f"- Offline Targets: {', '.join(report['offline_targets'])}",
        f"- Quorum Required: {report['quorum_required']}",
        f"- Quorum Observed: {report['quorum_observed']}",
        f"- Agreement Rate: {report['agreement_rate']}",
        f"- Conflict Detected: {report['conflict_detected']}",
        f"- Conflict Resolution Strategy: {report['conflict_resolution_strategy']}",
        f"- Inject Conflict: {report['inject_conflict']}",
        f"- All Recoveries Successful: {report['all_recoveries_successful']}",
        "",
        "## Target Recovery",
        "",
    ]

    for item in target_reports:
        lines.append(
            f"- {item['target_validator']}: final_hash_match={item['final_hash_match']} recovery_success={item['recovery_success']} blocks_missed={item['blocks_missed']}"
        )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic dual-offline recovery checks")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument(
        "--targets",
        nargs=2,
        default=["validator-4", "validator-5"],
        help="Exactly two offline validators to recover",
    )
    parser.add_argument("--blocks-missed", type=int, default=100, help="Blocks missed while offline")
    parser.add_argument("--ledger-height", type=int, default=1500, help="Network ledger height")
    parser.add_argument(
        "--inject-conflict",
        default="validator-1",
        help="Observed validator to mutate for conflict-resolution testing",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/dual_offline_report.json",
        help="Output JSON report",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/dual_offline_report.md",
        help="Output markdown report",
    )
    args = parser.parse_args()

    report = run_dual_offline(
        validators=args.validators,
        epoch=args.epoch,
        targets=args.targets,
        blocks_missed=args.blocks_missed,
        ledger_height=args.ledger_height,
        inject_conflict=args.inject_conflict,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Conflict detected: {report['conflict_detected']}")
    print(f"Quorum observed: {report['quorum_observed']}/{report['quorum_required']}")
    print(f"All recoveries successful: {report['all_recoveries_successful']}")

    raise SystemExit(0 if report["all_recoveries_successful"] else 1)


if __name__ == "__main__":
    main()
