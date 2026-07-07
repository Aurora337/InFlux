#!/usr/bin/env python3
"""Validate deterministic sync operations governance report integrity and consistency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


KNOWN_APPROVAL_MODES = {"approved", "conditional", "blocked"}
KNOWN_RELEASE_READINESS = {"ready", "ready_with_monitoring", "not_ready"}


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def _expected_approval_mode(readiness: str, blockers: list[str], pipeline_success: bool) -> str:
    if not pipeline_success or blockers or readiness == "not_ready":
        return "blocked"
    if readiness == "ready_with_monitoring":
        return "conditional"
    return "approved"


def _expected_signoffs(approval_mode: str) -> list[str]:
    if approval_mode == "blocked":
        return ["sync_oncall_lead", "platform_reliability_lead", "release_manager"]
    if approval_mode == "conditional":
        return ["sync_oncall_lead", "release_manager"]
    return ["release_manager"]


def validate_governance_report(
    assurance_report_path: Path,
    assurance_validation_path: Path,
    assurance_pipeline_path: Path,
    governance_report_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    assurance = _load_json(assurance_report_path)
    assurance_validation = _load_json(assurance_validation_path)
    pipeline = _load_json(assurance_pipeline_path)
    report = _load_json(governance_report_path)

    checks: list[dict] = []

    checks.append(_make_check("assurance_report_present", bool(assurance), f"path={assurance_report_path}"))
    checks.append(_make_check("assurance_validation_present", bool(assurance_validation), f"path={assurance_validation_path}"))
    checks.append(_make_check("assurance_pipeline_present", bool(pipeline), f"path={assurance_pipeline_path}"))
    checks.append(_make_check("governance_report_present", bool(report), f"path={governance_report_path}"))

    if assurance and assurance_validation and pipeline and report:
        checks.append(
            _make_check(
                "approval_mode_valid",
                report.get("approval_mode", "unknown") in KNOWN_APPROVAL_MODES,
                f"approval_mode={report.get('approval_mode', 'unknown')}",
            )
        )

        expected_mode = _expected_approval_mode(
            readiness=report.get("release_readiness", "not_ready"),
            blockers=report.get("governance_blockers", []),
            pipeline_success=bool(pipeline.get("pipeline_success", False)),
        )
        checks.append(
            _make_check(
                "approval_mode_consistent",
                report.get("approval_mode", "unknown") == expected_mode,
                f"report={report.get('approval_mode', 'unknown')} expected={expected_mode}",
            )
        )

        checks.append(
            _make_check(
                "release_readiness_valid",
                report.get("release_readiness", "unknown") in KNOWN_RELEASE_READINESS,
                f"release_readiness={report.get('release_readiness', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "release_readiness_consistent",
                report.get("release_readiness", "unknown") == assurance.get("release_readiness", "unknown"),
                f"report={report.get('release_readiness', 'unknown')} assurance={assurance.get('release_readiness', 'unknown')}",
            )
        )

        checks.append(
            _make_check(
                "assurance_score_consistent",
                int(report.get("assurance_score", 0)) == int(assurance.get("assurance_score", 0)),
                f"report={report.get('assurance_score', 0)} assurance={assurance.get('assurance_score', 0)}",
            )
        )
        checks.append(
            _make_check(
                "assurance_level_consistent",
                report.get("assurance_level", "unknown") == assurance.get("assurance_level", "unknown"),
                f"report={report.get('assurance_level', 'unknown')} assurance={assurance.get('assurance_level', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "pipeline_success_consistent",
                bool(report.get("pipeline_success", False)) == bool(pipeline.get("pipeline_success", False)),
                f"report={report.get('pipeline_success', False)} pipeline={pipeline.get('pipeline_success', False)}",
            )
        )

        expected_signoffs = _expected_signoffs(report.get("approval_mode", "blocked"))
        checks.append(
            _make_check(
                "required_signoffs_consistent",
                report.get("required_signoffs", []) == expected_signoffs,
                f"report={report.get('required_signoffs', [])} expected={expected_signoffs}",
            )
        )

        checks.append(
            _make_check(
                "governance_actions_non_empty",
                len(report.get("governance_actions", [])) > 0,
                f"governance_actions_count={len(report.get('governance_actions', []))}",
            )
        )

        checks.append(
            _make_check(
                "checks_count_consistent",
                int(report.get("checks_total", 0)) == len(report.get("checks", [])),
                f"checks_total={report.get('checks_total', 0)} checks_len={len(report.get('checks', []))}",
            )
        )
        checks.append(
            _make_check(
                "checks_arithmetic_consistent",
                int(report.get("checks_passed", 0)) + int(report.get("checks_failed", 0)) == int(report.get("checks_total", 0)),
                (
                    f"passed={report.get('checks_passed', 0)} "
                    f"failed={report.get('checks_failed', 0)} "
                    f"total={report.get('checks_total', 0)}"
                ),
            )
        )

    failed = [item for item in checks if not item["passed"]]
    report_valid = len(failed) == 0

    validation = {
        "suite": "v0.9.3-sync-ops-governance-report-validator",
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
        "# v0.9.3 Sync Ops Governance Report Validation",
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
    parser = argparse.ArgumentParser(description="Validate deterministic sync ops governance report")
    parser.add_argument(
        "--assurance-report",
        default="testnet/launch/sync_ops_assurance_report.json",
        help="Assurance report JSON path",
    )
    parser.add_argument(
        "--assurance-validation",
        default="testnet/launch/sync_ops_assurance_report_validation.json",
        help="Assurance report validation JSON path",
    )
    parser.add_argument(
        "--assurance-pipeline",
        default="testnet/launch/sync_ops_assurance_pipeline.json",
        help="Assurance pipeline JSON path",
    )
    parser.add_argument(
        "--governance-report",
        default="testnet/launch/sync_ops_governance_report.json",
        help="Governance report JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_governance_report_validation.json",
        help="Validation JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_governance_report_validation.md",
        help="Validation markdown output path",
    )
    args = parser.parse_args()

    validation = validate_governance_report(
        assurance_report_path=Path(args.assurance_report),
        assurance_validation_path=Path(args.assurance_validation),
        assurance_pipeline_path=Path(args.assurance_pipeline),
        governance_report_path=Path(args.governance_report),
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
