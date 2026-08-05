#!/usr/bin/env python3
"""Validate deterministic sync-ops reproducibility manifest integrity and consistency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_REPRO_ARTIFACTS = [
    "testnet/launch/sync_ops_finalization_pipeline.json",
    "testnet/launch/sync_ops_release_gate.json",
    "testnet/launch/sync_ops_audit_log.json",
    "testnet/launch/sync_ops_audit_log_validation.json",
    "testnet/launch/sync_ops_audit_assurance_pipeline.json",
    "testnet/launch/sync_ops_audit_assurance_pipeline_validation.json",
    "testnet/launch/sync_ops_audit_assurance_validation_pipeline.json",
]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def validate_manifest(
    manifest_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    manifest = _load_json(manifest_path)

    checks: list[dict] = []
    checks.append(_make_check("manifest_present", bool(manifest), f"path={manifest_path}"))

    if manifest:
        run_one = manifest.get("replay_runs", [{}])[0] if manifest.get("replay_runs") else {}
        run_two = manifest.get("replay_runs", [{}, {}])[1] if len(manifest.get("replay_runs", [])) > 1 else {}
        run_1_artifacts = manifest.get("run_1_artifacts", [])
        run_2_artifacts = manifest.get("run_2_artifacts", [])
        checks_data = manifest.get("checks", [])
        terminal_summary = manifest.get("terminal_summary", {})

        checks.append(
            _make_check(
                "suite_name_expected",
                manifest.get("suite", "") == "v1.0.6-sync-ops-reproducibility-manifest",
                f"suite={manifest.get('suite', '')}",
            )
        )
        checks.append(
            _make_check(
                "replay_runs_count_expected",
                len(manifest.get("replay_runs", [])) == 2,
                f"replay_runs={len(manifest.get('replay_runs', []))}",
            )
        )
        checks.append(
            _make_check(
                "run_1_success",
                bool(run_one.get("success", False)),
                f"run_1_success={run_one.get('success', False)}",
            )
        )
        checks.append(
            _make_check(
                "run_2_success",
                bool(run_two.get("success", False)),
                f"run_2_success={run_two.get('success', False)}",
            )
        )

        checks.append(
            _make_check(
                "artifacts_count_consistent",
                len(run_1_artifacts) == len(EXPECTED_REPRO_ARTIFACTS) and len(run_2_artifacts) == len(EXPECTED_REPRO_ARTIFACTS),
                f"run1={len(run_1_artifacts)} run2={len(run_2_artifacts)} expected={len(EXPECTED_REPRO_ARTIFACTS)}",
            )
        )

        run_1_paths = [item.get("path", "") for item in run_1_artifacts]
        run_2_paths = [item.get("path", "") for item in run_2_artifacts]
        checks.append(
            _make_check(
                "run_1_paths_expected",
                run_1_paths == EXPECTED_REPRO_ARTIFACTS,
                f"observed={run_1_paths} expected={EXPECTED_REPRO_ARTIFACTS}",
            )
        )
        checks.append(
            _make_check(
                "run_2_paths_expected",
                run_2_paths == EXPECTED_REPRO_ARTIFACTS,
                f"observed={run_2_paths} expected={EXPECTED_REPRO_ARTIFACTS}",
            )
        )

        mismatch_paths: list[str] = []
        if run_1_artifacts and run_2_artifacts and len(run_1_artifacts) == len(run_2_artifacts):
            for idx, item_one in enumerate(run_1_artifacts):
                item_two = run_2_artifacts[idx]
                path = item_one.get("path", "unknown")
                same = (
                    bool(item_one.get("exists", False)) == bool(item_two.get("exists", False))
                    and item_one.get("sha256", "") == item_two.get("sha256", "")
                    and int(item_one.get("size_bytes", 0)) == int(item_two.get("size_bytes", 0))
                )
                checks.append(
                    _make_check(
                        f"artifact_reproducible::{path}",
                        same,
                        (
                            f"exists={item_one.get('exists', False)}/{item_two.get('exists', False)} "
                            f"size={item_one.get('size_bytes', 0)}/{item_two.get('size_bytes', 0)} "
                            f"sha={item_one.get('sha256', '')}/{item_two.get('sha256', '')}"
                        ),
                    )
                )
                if not same:
                    mismatch_paths.append(path)

        checks.append(
            _make_check(
                "mismatch_paths_consistent",
                sorted(manifest.get("mismatch_paths", [])) == sorted(mismatch_paths),
                f"manifest={sorted(manifest.get('mismatch_paths', []))} computed={sorted(mismatch_paths)}",
            )
        )

        failed_from_checks = [item for item in checks_data if not item.get("passed", False)]
        computed_failed = [item for item in checks if not item["passed"]]
        checks.append(
            _make_check(
                "checks_total_consistent",
                int(manifest.get("checks_total", 0)) == len(checks_data),
                f"manifest={manifest.get('checks_total', 0)} computed={len(checks_data)}",
            )
        )
        checks.append(
            _make_check(
                "checks_failed_consistent",
                int(manifest.get("checks_failed", 0)) == len(failed_from_checks),
                f"manifest={manifest.get('checks_failed', 0)} computed={len(failed_from_checks)}",
            )
        )
        checks.append(
            _make_check(
                "checks_passed_consistent",
                int(manifest.get("checks_passed", 0)) == (len(checks_data) - len(failed_from_checks)),
                (
                    f"manifest={manifest.get('checks_passed', 0)} "
                    f"computed={len(checks_data) - len(failed_from_checks)}"
                ),
            )
        )

        failed_check_names = [item["check"] for item in failed_from_checks]
        checks.append(
            _make_check(
                "failed_checks_list_consistent",
                sorted(manifest.get("failed_checks", [])) == sorted(failed_check_names),
                f"manifest={sorted(manifest.get('failed_checks', []))} computed={sorted(failed_check_names)}",
            )
        )

        checks.append(
            _make_check(
                "reproducible_flag_consistent",
                bool(manifest.get("reproducible", False)) == (len(failed_from_checks) == 0),
                f"reproducible={manifest.get('reproducible', False)} failed={len(failed_from_checks)}",
            )
        )

        terminal_report = _load_json(Path("testnet/launch/sync_ops_audit_assurance_validation_pipeline.json"))
        terminal_report_summary = terminal_report.get("summary", {}) if terminal_report else {}
        checks.append(
            _make_check(
                "terminal_summary_release_decision_consistent",
                terminal_summary.get("release_decision", "unknown")
                == terminal_report_summary.get("release_decision", "unknown"),
                (
                    f"manifest={terminal_summary.get('release_decision', 'unknown')} "
                    f"report={terminal_report_summary.get('release_decision', 'unknown')}"
                ),
            )
        )
        checks.append(
            _make_check(
                "terminal_summary_audit_valid_consistent",
                bool(terminal_summary.get("audit_valid", False))
                == bool(terminal_report_summary.get("audit_valid", False)),
                (
                    f"manifest={terminal_summary.get('audit_valid', False)} "
                    f"report={terminal_report_summary.get('audit_valid', False)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "terminal_summary_pipeline_validation_valid_consistent",
                bool(terminal_summary.get("pipeline_validation_valid", False))
                == bool(terminal_report_summary.get("pipeline_validation_valid", False)),
                (
                    f"manifest={terminal_summary.get('pipeline_validation_valid', False)} "
                    f"report={terminal_report_summary.get('pipeline_validation_valid', False)}"
                ),
            )
        )

    failed = [item for item in checks if not item["passed"]]
    manifest_valid = len(failed) == 0

    validation = {
        "suite": "v1.0.7-sync-ops-reproducibility-manifest-validator",
        "manifest_valid": manifest_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.7 Sync Ops Reproducibility Manifest Validation",
        "",
        f"- Manifest Valid: {validation['manifest_valid']}",
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
    parser = argparse.ArgumentParser(description="Validate deterministic sync-ops reproducibility manifest")
    parser.add_argument(
        "--manifest",
        default="testnet/launch/sync_ops_reproducibility_manifest.json",
        help="Reproducibility manifest JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_reproducibility_manifest_validation.json",
        help="Validation JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_reproducibility_manifest_validation.md",
        help="Validation markdown output path",
    )
    args = parser.parse_args()

    validation = validate_manifest(
        manifest_path=Path(args.manifest),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Manifest Valid: {validation['manifest_valid']}")
    print(f"Checks Passed: {validation['checks_passed']}/{validation['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()