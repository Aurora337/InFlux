#!/usr/bin/env python3
"""Run deterministic v0.7 fault scenarios and aggregate results."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEALTH_PATH = ROOT / "testnet/launch/network_health.json"


def _run_launch(validators: int, epoch: int, fault_mode: str, fault_validator: str) -> tuple[int, str]:
    command = [
        sys.executable,
        "launch_testnet.py",
        "--validators",
        str(validators),
        "--epoch",
        str(epoch),
        "--fault-mode",
        fault_mode,
    ]
    if fault_validator:
        command.extend(["--fault-validator", fault_validator])

    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return completed.returncode, completed.stdout.strip()


def _load_health() -> dict:
    if not HEALTH_PATH.exists():
        return {}
    return json.loads(HEALTH_PATH.read_text(encoding="utf-8"))


def _evaluate(name: str, health: dict) -> tuple[bool, str]:
    if not health:
        return False, "missing_health_artifact"

    if name == "baseline":
        if health.get("network_status") != "healthy":
            return False, "baseline_not_healthy"
        if float(health.get("handshake_completion_rate", 0.0)) != 1.0:
            return False, "baseline_handshake_incomplete"
        return True, "ok"

    if health.get("network_status") != "unhealthy":
        return False, "fault_not_detected"

    if name == "snapshot_hash_mismatch" and int(health.get("divergence_count", 0)) <= 0:
        return False, "missing_divergence"

    if name == "message_hash_mismatch" and int(health.get("invalid_message_count", 0)) <= 0:
        return False, "missing_invalid_messages"

    if name == "drop_outbound" and int(health.get("missing_message_count", 0)) <= 0:
        return False, "missing_message_gap"

    return True, "ok"


def run_fault_suite(validators: int, epoch: int, fault_validator: str) -> dict:
    scenarios = [
        {"name": "baseline", "fault_mode": "none", "fault_validator": ""},
        {
            "name": "snapshot_hash_mismatch",
            "fault_mode": "snapshot_hash_mismatch",
            "fault_validator": fault_validator,
        },
        {
            "name": "message_hash_mismatch",
            "fault_mode": "message_hash_mismatch",
            "fault_validator": fault_validator,
        },
        {
            "name": "drop_outbound",
            "fault_mode": "drop_outbound",
            "fault_validator": fault_validator,
        },
    ]

    results: list[dict] = []
    for scenario in scenarios:
        return_code, stdout = _run_launch(
            validators=validators,
            epoch=epoch,
            fault_mode=scenario["fault_mode"],
            fault_validator=scenario["fault_validator"],
        )
        health = _load_health()
        passed, reason = _evaluate(scenario["name"], health)

        results.append(
            {
                "scenario": scenario["name"],
                "fault_mode": scenario["fault_mode"],
                "fault_validator": scenario["fault_validator"],
                "launch_exit_code": return_code,
                "evaluation_passed": passed,
                "evaluation_reason": reason,
                "health": {
                    "consensus_status": health.get("consensus_status"),
                    "network_status": health.get("network_status"),
                    "consensus_rate": health.get("consensus_rate"),
                    "agreement_rate": health.get("agreement_rate"),
                    "hash_agreement_rate": health.get("hash_agreement_rate"),
                    "divergence_count": health.get("divergence_count"),
                    "message_count": health.get("message_count"),
                    "expected_message_count": health.get("expected_message_count"),
                    "handshake_completion_rate": health.get("handshake_completion_rate"),
                    "invalid_message_count": health.get("invalid_message_count"),
                    "missing_message_count": health.get("missing_message_count"),
                },
                "launch_output": stdout.splitlines(),
            }
        )

    scenarios_passed = sum(1 for item in results if item["evaluation_passed"])
    scenarios_checked = len(results)
    return {
        "suite": "v0.7.5-fault-suite",
        "validators": validators,
        "epoch": epoch,
        "fault_validator": fault_validator,
        "scenarios_checked": scenarios_checked,
        "scenarios_passed": scenarios_passed,
        "scenarios_failed": scenarios_checked - scenarios_passed,
        "overall_status": "PASS" if scenarios_passed == scenarios_checked else "FAIL",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic fault scenarios")
    parser.add_argument("--validators", type=int, default=5, help="Number of validators")
    parser.add_argument("--epoch", type=int, default=1, help="Epoch used for snapshots")
    parser.add_argument(
        "--fault-validator",
        default="validator-3",
        help="Validator id used for injected fault scenarios",
    )
    parser.add_argument(
        "--output",
        default="testnet/launch/fault_report.json",
        help="Path to write fault suite report",
    )
    args = parser.parse_args()

    report = run_fault_suite(args.validators, args.epoch, args.fault_validator)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Fault scenarios checked: {report['scenarios_checked']}")
    print(f"Fault scenarios passed: {report['scenarios_passed']}")
    print(f"Fault scenarios failed: {report['scenarios_failed']}")
    print(f"Overall status: {report['overall_status']}")
    print(f"Report: {output_path}")

    raise SystemExit(0 if report["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
