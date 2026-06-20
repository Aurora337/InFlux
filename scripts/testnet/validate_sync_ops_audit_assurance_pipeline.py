#!/usr/bin/env python3
"""Validate deterministic sync ops audit assurance pipeline integrity and consistency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_STEPS = [
    "finalization_pipeline",
    "release_gate",
    "audit_log",
    "audit_validation",
]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def validate_pipeline(
    pipeline_path: Path,
    finalization_path: Path,
    release_gate_path: Path,
    audit_log_path: Path,
    audit_validation_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    pipeline = _load_json(pipeline_path)
    finalization = _load_json(finalization_path)
    gate = _load_json(release_gate_path)
    audit = _load_json(audit_log_path)
    audit_validation = _load_json(audit_validation_path)

    checks: list[dict] = []

    checks.append(_make_check("pipeline_report_present", bool(pipeline), f"path={pipeline_path}"))
    checks.append(_make_check("finalization_present", bool(finalization), f"path={finalization_path}"))
    checks.append(_make_check("release_gate_present", bool(gate), f"path={release_gate_path}"))
    checks.append(_make_check("audit_log_present", bool(audit), f"path={audit_log_path}"))
    checks.append(_make_check("audit_validation_present", bool(audit_validation), f"path={audit_validation_path}"))

    if pipeline and finalization and gate and audit and audit_validation:
        stage_results = pipeline.get("stage_results", [])
        observed_steps = [item.get("step", "") for item in stage_results]
        summary = pipeline.get("summary", {})

        checks.append(
            _make_check(
                "suite_name_expected",
                pipeline.get("suite", "") == "v1.0.3-sync-ops-audit-assurance-pipeline",
                f"suite={pipeline.get('suite', '')}",
            )
        )
        checks.append(
            _make_check(
                "stages_total_expected",
                int(pipeline.get("stages_total", 0)) == len(EXPECTED_STEPS),
                f"stages_total={pipeline.get('stages_total', 0)} expected={len(EXPECTED_STEPS)}",
            )
        )
        checks.append(
            _make_check(
                "stages_executed_consistent",
                int(pipeline.get("stages_executed", 0)) == len(stage_results),
                f"stages_executed={pipeline.get('stages_executed', 0)} observed={len(stage_results)}",
            )
        )
        checks.append(
            _make_check(
                "stages_succeeded_consistent",
                int(pipeline.get("stages_succeeded", 0)) == sum(1 for item in stage_results if bool(item.get("success", False))),
                (
                    f"stages_succeeded={pipeline.get('stages_succeeded', 0)} "
                    f"computed={sum(1 for item in stage_results if bool(item.get('success', False)))}"
                ),
            )
        )
        checks.append(
            _make_check(
                "stage_sequence_expected",
                observed_steps == EXPECTED_STEPS[: len(observed_steps)],
                f"observed={observed_steps} expected_prefix={EXPECTED_STEPS[: len(observed_steps)]}",
            )
        )

        expected_failed_stage = next((item.get("step", "unknown") for item in stage_results if not item.get("success", False)), "none")
        checks.append(
            _make_check(
                "failed_stage_consistent",
                pipeline.get("failed_stage", "none") == expected_failed_stage,
                f"report={pipeline.get('failed_stage', 'none')} computed={expected_failed_stage}",
            )
        )
        checks.append(
            _make_check(
                "pipeline_success_consistent_with_stages",
                bool(pipeline.get("pipeline_success", False)) == all(bool(item.get("success", False)) for item in stage_results),
                f"pipeline_success={pipeline.get('pipeline_success', False)}",
            )
        )

        checks.append(
            _make_check(
                "release_decision_consistent",
                summary.get("release_decision", "unknown") == gate.get("release_decision", "unknown"),
                f"summary={summary.get('release_decision', 'unknown')} gate={gate.get('release_decision', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "certificate_status_consistent",
                summary.get("certificate_status", "unknown") == finalization.get("terminal_summary", {}).get("certificate_status", "unknown"),
                (
                    f"summary={summary.get('certificate_status', 'unknown')} "
                    f"finalization={finalization.get('terminal_summary', {}).get('certificate_status', 'unknown')}"
                ),
            )
        )
        checks.append(
            _make_check(
                "certificate_valid_consistent",
                bool(summary.get("certificate_valid", False)) == bool(finalization.get("terminal_summary", {}).get("certificate_valid", False)),
                (
                    f"summary={summary.get('certificate_valid', False)} "
                    f"finalization={finalization.get('terminal_summary', {}).get('certificate_valid', False)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "fingerprint_consistent",
                summary.get("certificate_fingerprint", "") == gate.get("certificate_fingerprint", ""),
                (
                    f"summary={summary.get('certificate_fingerprint', '')} "
                    f"gate={gate.get('certificate_fingerprint', '')}"
                ),
            )
        )
        checks.append(
            _make_check(
                "assurance_score_consistent",
                int(summary.get("assurance_score", 0)) == int(gate.get("assurance_score", 0)),
                f"summary={summary.get('assurance_score', 0)} gate={gate.get('assurance_score', 0)}",
            )
        )
        checks.append(
            _make_check(
                "approval_mode_consistent",
                summary.get("approval_mode", "unknown") == gate.get("approval_mode", "unknown"),
                f"summary={summary.get('approval_mode', 'unknown')} gate={gate.get('approval_mode', 'unknown')}",
            )
        )

        checks.append(
            _make_check(
                "audit_complete_consistent",
                bool(summary.get("audit_complete", False)) == bool(audit.get("audit_complete", False)),
                f"summary={summary.get('audit_complete', False)} audit={audit.get('audit_complete', False)}",
            )
        )
        checks.append(
            _make_check(
                "artifacts_present_consistent",
                int(summary.get("artifacts_present", 0)) == int(audit.get("artifacts_present", 0))
                and int(summary.get("artifacts_expected", 0)) == int(audit.get("artifacts_expected", 0)),
                (
                    f"summary={summary.get('artifacts_present', 0)}/{summary.get('artifacts_expected', 0)} "
                    f"audit={audit.get('artifacts_present', 0)}/{audit.get('artifacts_expected', 0)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "audit_valid_consistent",
                bool(summary.get("audit_valid", False)) == bool(audit_validation.get("audit_valid", False)),
                f"summary={summary.get('audit_valid', False)} validation={audit_validation.get('audit_valid', False)}",
            )
        )
        checks.append(
            _make_check(
                "audit_checks_consistent",
                int(summary.get("audit_checks_passed", 0)) == int(audit_validation.get("checks_passed", 0))
                and int(summary.get("audit_checks_total", 0)) == int(audit_validation.get("checks_total", 0)),
                (
                    f"summary={summary.get('audit_checks_passed', 0)}/{summary.get('audit_checks_total', 0)} "
                    f"validation={audit_validation.get('checks_passed', 0)}/{audit_validation.get('checks_total', 0)}"
                ),
            )
        )

        artifact_manifest = pipeline.get("artifact_manifest", [])
        checks.append(
            _make_check(
                "artifact_manifest_count_expected",
                len(artifact_manifest) == len(EXPECTED_STEPS),
                f"manifest_count={len(artifact_manifest)} expected={len(EXPECTED_STEPS)}",
            )
        )

        expected_paths = [
            "testnet/launch/sync_ops_finalization_pipeline.json",
            "testnet/launch/sync_ops_release_gate.json",
            "testnet/launch/sync_ops_audit_log.json",
            "testnet/launch/sync_ops_audit_log_validation.json",
        ]
        observed_paths = [item.get("path", "") for item in artifact_manifest]
        checks.append(
            _make_check(
                "artifact_manifest_paths_expected",
                observed_paths == expected_paths,
                f"observed={observed_paths} expected={expected_paths}",
            )
        )

        for item in artifact_manifest:
            path = Path(item.get("path", ""))
            exists = path.exists()
            checks.append(
                _make_check(
                    f"artifact_presence_consistent::{item.get('path', '')}",
                    bool(item.get("exists", False)) == exists,
                    f"manifest={item.get('exists', False)} filesystem={exists}",
                )
            )

    failed = [item for item in checks if not item["passed"]]
    pipeline_valid = len(failed) == 0

    validation = {
        "suite": "v1.0.4-sync-ops-audit-assurance-pipeline-validator",
        "pipeline_valid": pipeline_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.4 Sync Ops Audit Assurance Pipeline Validation",
        "",
        f"- Pipeline Valid: {validation['pipeline_valid']}",
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
    parser = argparse.ArgumentParser(description="Validate deterministic sync ops audit assurance pipeline")
    parser.add_argument(
        "--pipeline",
        default="testnet/launch/sync_ops_audit_assurance_pipeline.json",
        help="Audit assurance pipeline JSON path",
    )
    parser.add_argument(
        "--finalization",
        default="testnet/launch/sync_ops_finalization_pipeline.json",
        help="Finalization pipeline JSON path",
    )
    parser.add_argument(
        "--release-gate",
        default="testnet/launch/sync_ops_release_gate.json",
        help="Release gate JSON path",
    )
    parser.add_argument(
        "--audit-log",
        default="testnet/launch/sync_ops_audit_log.json",
        help="Audit log JSON path",
    )
    parser.add_argument(
        "--audit-validation",
        default="testnet/launch/sync_ops_audit_log_validation.json",
        help="Audit log validation JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_audit_assurance_pipeline_validation.json",
        help="Validation JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_audit_assurance_pipeline_validation.md",
        help="Validation markdown output path",
    )
    args = parser.parse_args()

    validation = validate_pipeline(
        pipeline_path=Path(args.pipeline),
        finalization_path=Path(args.finalization),
        release_gate_path=Path(args.release_gate),
        audit_log_path=Path(args.audit_log),
        audit_validation_path=Path(args.audit_validation),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Pipeline Valid: {validation['pipeline_valid']}")
    print(f"Checks Passed: {validation['checks_passed']}/{validation['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()