#!/usr/bin/env python3
"""Generate deterministic sync operations assurance report from validation artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


KNOWN_STATES = {"stable", "degraded_recovered", "critical"}


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _assurance_level(score: int) -> str:
    if score >= 90:
        return "high"
    if score >= 75:
        return "medium"
    return "low"


def _release_readiness(assurance_level: str, release_blockers: list[str], decision: str) -> str:
    if release_blockers:
        return "not_ready"
    if decision == "promote_with_monitoring" or assurance_level == "medium":
        return "ready_with_monitoring"
    return "ready"


def generate_assurance_report(
    runbook_path: Path,
    gate_path: Path,
    packet_path: Path,
    packet_validation_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    runbook = _load_json(runbook_path)
    gate = _load_json(gate_path)
    packet = _load_json(packet_path)
    packet_validation = _load_json(packet_validation_path)

    checks: list[dict] = []

    checks.append({"check": "runbook_present", "passed": bool(runbook), "details": f"path={runbook_path}"})
    checks.append({"check": "gate_present", "passed": bool(gate), "details": f"path={gate_path}"})
    checks.append({"check": "packet_present", "passed": bool(packet), "details": f"path={packet_path}"})
    checks.append(
        {
            "check": "packet_validation_present",
            "passed": bool(packet_validation),
            "details": f"path={packet_validation_path}",
        }
    )

    if runbook and gate and packet and packet_validation:
        checks.append(
            {
                "check": "operational_state_known",
                "passed": runbook.get("operational_state", "unknown") in KNOWN_STATES,
                "details": f"state={runbook.get('operational_state', 'unknown')}",
            }
        )
        checks.append(
            {
                "check": "stability_gate_passed",
                "passed": bool(gate.get("gate_passed", False)),
                "details": f"gate_passed={gate.get('gate_passed', False)}",
            }
        )
        checks.append(
            {
                "check": "packet_validator_passed",
                "passed": bool(packet_validation.get("packet_valid", False)),
                "details": f"packet_valid={packet_validation.get('packet_valid', False)}",
            }
        )
        checks.append(
            {
                "check": "decision_recommendation_aligned",
                "passed": packet.get("promotion_decision", "hold") == packet.get("promotion_recommendation", "hold"),
                "details": (
                    f"decision={packet.get('promotion_decision', 'hold')} "
                    f"recommendation={packet.get('promotion_recommendation', 'hold')}"
                ),
            }
        )
        checks.append(
            {
                "check": "packet_has_no_blockers",
                "passed": len(packet.get("blockers", [])) == 0,
                "details": f"blockers={packet.get('blockers', [])}",
            }
        )
        checks.append(
            {
                "check": "packet_validation_no_failed_checks",
                "passed": len(packet_validation.get("failed_checks", [])) == 0,
                "details": f"failed_checks={packet_validation.get('failed_checks', [])}",
            }
        )

    failed_checks = [item for item in checks if not item["passed"]]

    score = 100
    score -= len(failed_checks) * 12

    if runbook.get("operational_state") == "degraded_recovered":
        score -= 8
    if runbook.get("operational_state") == "critical":
        score -= 25
    if bool(gate.get("escalated", False)):
        score -= 20

    if score < 0:
        score = 0
    if score > 100:
        score = 100

    assurance_level = _assurance_level(score)
    release_blockers: list[str] = []
    if failed_checks:
        release_blockers.extend(item["check"] for item in failed_checks)
    if packet.get("blockers"):
        release_blockers.extend([f"packet::{item}" for item in packet.get("blockers", [])])

    # Keep deterministic ordering and uniqueness.
    release_blockers = sorted(set(release_blockers))

    release_readiness = _release_readiness(
        assurance_level=assurance_level,
        release_blockers=release_blockers,
        decision=packet.get("promotion_decision", "hold"),
    )

    report = {
        "suite": "v0.9.2-sync-ops-assurance-report",
        "assurance_score": score,
        "assurance_level": assurance_level,
        "release_readiness": release_readiness,
        "promotion_decision": packet.get("promotion_decision", "hold"),
        "promotion_recommendation": packet.get("promotion_recommendation", "hold"),
        "operational_state": runbook.get("operational_state", "unknown"),
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed_checks),
        "checks_failed": len(failed_checks),
        "failed_checks": [item["check"] for item in failed_checks],
        "release_blockers": release_blockers,
        "input_summary": {
            "gate_passed": bool(gate.get("gate_passed", False)),
            "readiness_score": int(gate.get("readiness_score", 0)),
            "packet_valid": bool(packet_validation.get("packet_valid", False)),
            "packet_validation_checks_passed": packet_validation.get("checks_passed", 0),
            "packet_validation_checks_total": packet_validation.get("checks_total", 0),
        },
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.2 Sync Ops Assurance Report",
        "",
        f"- Assurance Score: {report['assurance_score']}",
        f"- Assurance Level: {report['assurance_level']}",
        f"- Release Readiness: {report['release_readiness']}",
        f"- Promotion Decision: {report['promotion_decision']}",
        f"- Promotion Recommendation: {report['promotion_recommendation']}",
        f"- Operational State: {report['operational_state']}",
        f"- Checks: {report['checks_passed']}/{report['checks_total']}",
        "",
        "## Input Summary",
        "",
        f"- gate_passed={report['input_summary']['gate_passed']}",
        f"- readiness_score={report['input_summary']['readiness_score']}",
        f"- packet_valid={report['input_summary']['packet_valid']}",
        (
            "- packet_validation_checks="
            f"{report['input_summary']['packet_validation_checks_passed']}/"
            f"{report['input_summary']['packet_validation_checks_total']}"
        ),
        "",
        "## Release Blockers",
        "",
    ]

    if report["release_blockers"]:
        for blocker in report["release_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")

    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync ops assurance report")
    parser.add_argument("--runbook", default="testnet/launch/sync_ops_runbook.json", help="Runbook JSON path")
    parser.add_argument("--gate", default="testnet/launch/sync_ops_stability_gate.json", help="Stability gate JSON path")
    parser.add_argument("--packet", default="testnet/launch/sync_ops_promotion_packet.json", help="Promotion packet JSON path")
    parser.add_argument(
        "--packet-validation",
        default="testnet/launch/sync_ops_promotion_packet_validation.json",
        help="Promotion packet validation JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_assurance_report.json",
        help="Assurance report JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_assurance_report.md",
        help="Assurance report markdown output path",
    )
    args = parser.parse_args()

    report = generate_assurance_report(
        runbook_path=Path(args.runbook),
        gate_path=Path(args.gate),
        packet_path=Path(args.packet),
        packet_validation_path=Path(args.packet_validation),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Assurance Score: {report['assurance_score']}")
    print(f"Assurance Level: {report['assurance_level']}")
    print(f"Release Readiness: {report['release_readiness']}")
    print(f"Checks Passed: {report['checks_passed']}/{report['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
