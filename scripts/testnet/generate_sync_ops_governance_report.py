#!/usr/bin/env python3
"""Generate deterministic sync operations governance report from assurance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _approval_mode(readiness: str, blockers: list[str], pipeline_success: bool) -> str:
    if not pipeline_success or blockers or readiness == "not_ready":
        return "blocked"
    if readiness == "ready_with_monitoring":
        return "conditional"
    return "approved"


def _required_signoffs(approval_mode: str) -> list[str]:
    if approval_mode == "blocked":
        return [
            "sync_oncall_lead",
            "platform_reliability_lead",
            "release_manager",
        ]
    if approval_mode == "conditional":
        return [
            "sync_oncall_lead",
            "release_manager",
        ]
    return [
        "release_manager",
    ]


def _governance_actions(approval_mode: str, readiness: str) -> list[str]:
    if approval_mode == "blocked":
        return [
            "Block production promotion until all governance blockers are resolved.",
            "Re-run assurance pipeline after corrective actions and archive updated artifacts.",
            "Escalate unresolved blockers to governance review board.",
        ]
    if approval_mode == "conditional":
        return [
            "Allow promotion with heightened monitoring window.",
            "Require checkpoint review after first post-release sync cycle.",
            "Attach governance report and assurance artifacts to release notes.",
        ]
    if readiness == "ready":
        return [
            "Proceed with standard release controls and artifact retention.",
            "Log governance approval for audit traceability.",
        ]
    return [
        "Proceed with release after required sign-offs.",
    ]


def generate_governance_report(
    assurance_report_path: Path,
    assurance_validation_path: Path,
    assurance_pipeline_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    assurance = _load_json(assurance_report_path)
    assurance_validation = _load_json(assurance_validation_path)
    pipeline = _load_json(assurance_pipeline_path)

    checks: list[dict] = []

    checks.append({"check": "assurance_report_present", "passed": bool(assurance), "details": f"path={assurance_report_path}"})
    checks.append(
        {
            "check": "assurance_validation_present",
            "passed": bool(assurance_validation),
            "details": f"path={assurance_validation_path}",
        }
    )
    checks.append(
        {
            "check": "assurance_pipeline_present",
            "passed": bool(pipeline),
            "details": f"path={assurance_pipeline_path}",
        }
    )

    if assurance and assurance_validation and pipeline:
        checks.append(
            {
                "check": "assurance_validation_passed",
                "passed": bool(assurance_validation.get("report_valid", False)),
                "details": f"report_valid={assurance_validation.get('report_valid', False)}",
            }
        )
        checks.append(
            {
                "check": "pipeline_success",
                "passed": bool(pipeline.get("pipeline_success", False)),
                "details": f"pipeline_success={pipeline.get('pipeline_success', False)}",
            }
        )
        checks.append(
            {
                "check": "assurance_score_threshold",
                "passed": int(assurance.get("assurance_score", 0)) >= 75,
                "details": f"assurance_score={assurance.get('assurance_score', 0)} threshold=75",
            }
        )

    failed_checks = [item for item in checks if not item["passed"]]

    release_readiness = assurance.get("release_readiness", "not_ready")
    governance_blockers: list[str] = []
    governance_blockers.extend(assurance.get("release_blockers", []))

    if failed_checks:
        governance_blockers.extend([item["check"] for item in failed_checks])

    governance_blockers = sorted(set(governance_blockers))

    approval_mode = _approval_mode(
        readiness=release_readiness,
        blockers=governance_blockers,
        pipeline_success=bool(pipeline.get("pipeline_success", False)),
    )

    signoffs = _required_signoffs(approval_mode=approval_mode)
    actions = _governance_actions(approval_mode=approval_mode, readiness=release_readiness)

    report = {
        "suite": "v0.9.3-sync-ops-governance-report",
        "approval_mode": approval_mode,
        "release_readiness": release_readiness,
        "assurance_score": int(assurance.get("assurance_score", 0)),
        "assurance_level": assurance.get("assurance_level", "unknown"),
        "pipeline_success": bool(pipeline.get("pipeline_success", False)),
        "governance_blockers": governance_blockers,
        "required_signoffs": signoffs,
        "governance_actions": actions,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed_checks),
        "checks_failed": len(failed_checks),
        "failed_checks": [item["check"] for item in failed_checks],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.3 Sync Ops Governance Report",
        "",
        f"- Approval Mode: {report['approval_mode']}",
        f"- Release Readiness: {report['release_readiness']}",
        f"- Assurance Score: {report['assurance_score']}",
        f"- Assurance Level: {report['assurance_level']}",
        f"- Pipeline Success: {report['pipeline_success']}",
        f"- Checks: {report['checks_passed']}/{report['checks_total']}",
        "",
        "## Governance Blockers",
        "",
    ]

    if report["governance_blockers"]:
        for blocker in report["governance_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")

    lines.extend(["", "## Required Sign-Offs", ""])
    for signoff in report["required_signoffs"]:
        lines.append(f"- {signoff}")

    lines.extend(["", "## Governance Actions", ""])
    for action in report["governance_actions"]:
        lines.append(f"- {action}")

    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync ops governance report")
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
        "--output-json",
        default="testnet/launch/sync_ops_governance_report.json",
        help="Governance report JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_governance_report.md",
        help="Governance report markdown output path",
    )
    args = parser.parse_args()

    report = generate_governance_report(
        assurance_report_path=Path(args.assurance_report),
        assurance_validation_path=Path(args.assurance_validation),
        assurance_pipeline_path=Path(args.assurance_pipeline),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Approval Mode: {report['approval_mode']}")
    print(f"Release Readiness: {report['release_readiness']}")
    print(f"Checks Passed: {report['checks_passed']}/{report['checks_total']}")
    print(f"Blockers: {len(report['governance_blockers'])}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
