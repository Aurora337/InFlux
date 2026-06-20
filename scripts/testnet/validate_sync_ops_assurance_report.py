#!/usr/bin/env python3
"""Validate deterministic sync operations assurance report integrity and consistency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


KNOWN_ASSURANCE_LEVELS = {"high", "medium", "low"}
KNOWN_RELEASE_READINESS = {"ready", "ready_with_monitoring", "not_ready"}


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def _expected_assurance_level(score: int) -> str:
    if score >= 90:
        return "high"
    if score >= 75:
        return "medium"
    return "low"


def _expected_release_readiness(assurance_level: str, release_blockers: list[str], decision: str) -> str:
    if release_blockers:
        return "not_ready"
    if decision == "promote_with_monitoring" or assurance_level == "medium":
        return "ready_with_monitoring"
    return "ready"


def validate_assurance_report(
    runbook_path: Path,
    gate_path: Path,
    packet_path: Path,
    packet_validation_path: Path,
    assurance_report_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    runbook = _load_json(runbook_path)
    gate = _load_json(gate_path)
    packet = _load_json(packet_path)
    packet_validation = _load_json(packet_validation_path)
    report = _load_json(assurance_report_path)

    checks: list[dict] = []

    checks.append(_make_check("runbook_present", bool(runbook), f"path={runbook_path}"))
    checks.append(_make_check("gate_present", bool(gate), f"path={gate_path}"))
    checks.append(_make_check("packet_present", bool(packet), f"path={packet_path}"))
    checks.append(_make_check("packet_validation_present", bool(packet_validation), f"path={packet_validation_path}"))
    checks.append(_make_check("assurance_report_present", bool(report), f"path={assurance_report_path}"))

    if runbook and gate and packet and packet_validation and report:
        score = int(report.get("assurance_score", 0))
        expected_level = _expected_assurance_level(score)

        checks.append(
            _make_check(
                "assurance_level_valid",
                report.get("assurance_level", "unknown") in KNOWN_ASSURANCE_LEVELS,
                f"level={report.get('assurance_level', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "assurance_level_consistent",
                report.get("assurance_level", "unknown") == expected_level,
                f"level={report.get('assurance_level', 'unknown')} expected={expected_level}",
            )
        )
        checks.append(
            _make_check(
                "release_readiness_valid",
                report.get("release_readiness", "unknown") in KNOWN_RELEASE_READINESS,
                f"readiness={report.get('release_readiness', 'unknown')}",
            )
        )

        expected_readiness = _expected_release_readiness(
            assurance_level=report.get("assurance_level", "low"),
            release_blockers=report.get("release_blockers", []),
            decision=report.get("promotion_decision", "hold"),
        )
        checks.append(
            _make_check(
                "release_readiness_consistent",
                report.get("release_readiness", "unknown") == expected_readiness,
                f"readiness={report.get('release_readiness', 'unknown')} expected={expected_readiness}",
            )
        )

        checks.append(
            _make_check(
                "promotion_decision_consistent",
                report.get("promotion_decision", "hold") == packet.get("promotion_decision", "hold"),
                f"report={report.get('promotion_decision', 'hold')} packet={packet.get('promotion_decision', 'hold')}",
            )
        )
        checks.append(
            _make_check(
                "promotion_recommendation_consistent",
                report.get("promotion_recommendation", "hold") == packet.get("promotion_recommendation", "hold"),
                f"report={report.get('promotion_recommendation', 'hold')} packet={packet.get('promotion_recommendation', 'hold')}",
            )
        )
        checks.append(
            _make_check(
                "operational_state_consistent",
                report.get("operational_state", "unknown") == runbook.get("operational_state", "unknown"),
                f"report={report.get('operational_state', 'unknown')} runbook={runbook.get('operational_state', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "gate_summary_consistent",
                bool(report.get("input_summary", {}).get("gate_passed", False)) == bool(gate.get("gate_passed", False)),
                f"report={report.get('input_summary', {}).get('gate_passed', False)} gate={gate.get('gate_passed', False)}",
            )
        )
        checks.append(
            _make_check(
                "packet_validation_summary_consistent",
                bool(report.get("input_summary", {}).get("packet_valid", False)) == bool(packet_validation.get("packet_valid", False)),
                f"report={report.get('input_summary', {}).get('packet_valid', False)} packet_validation={packet_validation.get('packet_valid', False)}",
            )
        )
        checks.append(
            _make_check(
                "packet_validation_checks_consistent",
                int(report.get("input_summary", {}).get("packet_validation_checks_passed", 0))
                == int(packet_validation.get("checks_passed", 0))
                and int(report.get("input_summary", {}).get("packet_validation_checks_total", 0))
                == int(packet_validation.get("checks_total", 0)),
                (
                    f"report={report.get('input_summary', {}).get('packet_validation_checks_passed', 0)}/"
                    f"{report.get('input_summary', {}).get('packet_validation_checks_total', 0)} "
                    f"packet_validation={packet_validation.get('checks_passed', 0)}/"
                    f"{packet_validation.get('checks_total', 0)}"
                ),
            )
        )

        checks.append(
            _make_check(
                "checks_count_consistent",
                int(report.get("checks_total", 0)) == len(report.get("checks", [])),
                f"checks_total={report.get('checks_total', 0)} checks_len={len(report.get('checks', []))}",
            )
        )

        failed_checks = report.get("failed_checks", [])
        checks.append(
            _make_check(
                "failed_checks_count_consistent",
                int(report.get("checks_failed", 0)) == len(failed_checks),
                f"checks_failed={report.get('checks_failed', 0)} failed_len={len(failed_checks)}",
            )
        )
        checks.append(
            _make_check(
                "checks_passed_count_consistent",
                int(report.get("checks_passed", 0)) + int(report.get("checks_failed", 0)) == int(report.get("checks_total", 0)),
                (
                    f"checks_passed={report.get('checks_passed', 0)} "
                    f"checks_failed={report.get('checks_failed', 0)} "
                    f"checks_total={report.get('checks_total', 0)}"
                ),
            )
        )

    failed = [item for item in checks if not item["passed"]]
    report_valid = len(failed) == 0

    validation = {
        "suite": "v0.9.2-sync-ops-assurance-report-validator",
        "report_valid": report_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.2 Sync Ops Assurance Report Validation",
        "",
        f"- Report Valid: {validation['report_valid']}",
        f"- Checks Total: {validation['checks_total']}",
        f"- Checks Passed: {validation['checks_passed']}",
        f"- Checks Failed: {validation['checks_failed']}",
        "",
        "## Checks",
        "",
    ]

    for check in validation["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    if validation["failed_checks"]:
        lines.extend(["", "## Failed Checks", ""])
        for name in validation["failed_checks"]:
            lines.append(f"- {name}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return validation


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic sync ops assurance report")
    parser.add_argument("--runbook", default="testnet/launch/sync_ops_runbook.json", help="Runbook JSON path")
    parser.add_argument("--gate", default="testnet/launch/sync_ops_stability_gate.json", help="Stability gate JSON path")
    parser.add_argument("--packet", default="testnet/launch/sync_ops_promotion_packet.json", help="Promotion packet JSON path")
    parser.add_argument(
        "--packet-validation",
        default="testnet/launch/sync_ops_promotion_packet_validation.json",
        help="Promotion packet validation JSON path",
    )
    parser.add_argument(
        "--assurance-report",
        default="testnet/launch/sync_ops_assurance_report.json",
        help="Assurance report JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_assurance_report_validation.json",
        help="Validation JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_assurance_report_validation.md",
        help="Validation markdown output path",
    )
    args = parser.parse_args()

    validation = validate_assurance_report(
        runbook_path=Path(args.runbook),
        gate_path=Path(args.gate),
        packet_path=Path(args.packet),
        packet_validation_path=Path(args.packet_validation),
        assurance_report_path=Path(args.assurance_report),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Report Valid: {validation['report_valid']}")
    print(f"Checks Passed: {validation['checks_passed']}/{validation['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
