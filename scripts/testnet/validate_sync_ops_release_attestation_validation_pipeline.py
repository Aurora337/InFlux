#!/usr/bin/env python3
"""Validate deterministic sync-ops release-attestation validation pipeline integrity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_STAGE_SEQUENCE = [
    "reproducibility_validation_pipeline",
    "release_attestation",
    "release_attestation_validation",
]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def validate_pipeline(
    pipeline_path: Path,
    repro_pipeline_path: Path,
    attestation_path: Path,
    attestation_validation_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    pipeline = _load_json(pipeline_path)
    repro_pipeline = _load_json(repro_pipeline_path)
    attestation = _load_json(attestation_path)
    attestation_validation = _load_json(attestation_validation_path)

    checks: list[dict] = []
    checks.append(_make_check("pipeline_present", bool(pipeline), f"path={pipeline_path}"))
    checks.append(_make_check("repro_pipeline_present", bool(repro_pipeline), f"path={repro_pipeline_path}"))
    checks.append(_make_check("attestation_present", bool(attestation), f"path={attestation_path}"))
    checks.append(
        _make_check(
            "attestation_validation_present",
            bool(attestation_validation),
            f"path={attestation_validation_path}",
        )
    )

    if pipeline and repro_pipeline and attestation and attestation_validation:
        checks.append(
            _make_check(
                "suite_name_expected",
                pipeline.get("suite", "") == "v1.1.0-sync-ops-release-attestation-validation-pipeline",
                f"suite={pipeline.get('suite', '')}",
            )
        )

        stage_results = pipeline.get("stage_results", [])
        stage_names = [item.get("step", "") for item in stage_results]
        executed = len(stage_results)
        succeeded = sum(1 for item in stage_results if bool(item.get("success", False)))
        failed_stage_expected = next(
            (item.get("step", "") for item in stage_results if not bool(item.get("success", False))),
            "none",
        )

        checks.append(
            _make_check(
                "stages_total_expected",
                int(pipeline.get("stages_total", 0)) == len(EXPECTED_STAGE_SEQUENCE),
                f"observed={pipeline.get('stages_total', 0)} expected={len(EXPECTED_STAGE_SEQUENCE)}",
            )
        )
        checks.append(
            _make_check(
                "stages_executed_consistent",
                int(pipeline.get("stages_executed", 0)) == executed,
                f"observed={pipeline.get('stages_executed', 0)} computed={executed}",
            )
        )
        checks.append(
            _make_check(
                "stages_succeeded_consistent",
                int(pipeline.get("stages_succeeded", 0)) == succeeded,
                f"observed={pipeline.get('stages_succeeded', 0)} computed={succeeded}",
            )
        )
        checks.append(
            _make_check(
                "failed_stage_consistent",
                pipeline.get("failed_stage", "none") == failed_stage_expected,
                f"observed={pipeline.get('failed_stage', 'none')} computed={failed_stage_expected}",
            )
        )
        checks.append(
            _make_check(
                "stage_sequence_prefix_expected",
                stage_names == EXPECTED_STAGE_SEQUENCE[:executed],
                f"observed={stage_names} expected_prefix={EXPECTED_STAGE_SEQUENCE[:executed]}",
            )
        )

        summary = pipeline.get("summary", {})
        repro_summary = repro_pipeline.get("summary", {})

        checks.append(
            _make_check(
                "summary_release_version_consistent",
                summary.get("release_version", "unknown") == repro_summary.get("release_version", "unknown"),
                f"pipeline={summary.get('release_version', 'unknown')} repro={repro_summary.get('release_version', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "summary_release_decision_consistent",
                summary.get("release_decision", "unknown") == repro_summary.get("release_decision", "unknown"),
                f"pipeline={summary.get('release_decision', 'unknown')} repro={repro_summary.get('release_decision', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "summary_audit_valid_consistent",
                bool(summary.get("audit_valid", False)) == bool(repro_summary.get("audit_valid", False)),
                f"pipeline={summary.get('audit_valid', False)} repro={repro_summary.get('audit_valid', False)}",
            )
        )
        checks.append(
            _make_check(
                "summary_pipeline_validation_valid_consistent",
                bool(summary.get("pipeline_validation_valid", False))
                == bool(repro_summary.get("pipeline_validation_valid", False)),
                (
                    f"pipeline={summary.get('pipeline_validation_valid', False)} "
                    f"repro={repro_summary.get('pipeline_validation_valid', False)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "summary_reproducible_consistent",
                bool(summary.get("reproducible", False)) == bool(repro_summary.get("reproducible", False)),
                f"pipeline={summary.get('reproducible', False)} repro={repro_summary.get('reproducible', False)}",
            )
        )
        checks.append(
            _make_check(
                "summary_manifest_valid_consistent",
                bool(summary.get("manifest_valid", False)) == bool(repro_summary.get("manifest_valid", False)),
                f"pipeline={summary.get('manifest_valid', False)} repro={repro_summary.get('manifest_valid', False)}",
            )
        )
        checks.append(
            _make_check(
                "summary_attestation_status_consistent",
                summary.get("attestation_status", "unknown") == attestation.get("attestation_status", "unknown"),
                f"pipeline={summary.get('attestation_status', 'unknown')} attestation={attestation.get('attestation_status', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "summary_attestation_checks_consistent",
                int(summary.get("attestation_checks_passed", 0)) == int(attestation.get("checks_passed", 0))
                and int(summary.get("attestation_checks_total", 0)) == int(attestation.get("checks_total", 0)),
                (
                    f"pipeline={summary.get('attestation_checks_passed', 0)}/{summary.get('attestation_checks_total', 0)} "
                    f"attestation={attestation.get('checks_passed', 0)}/{attestation.get('checks_total', 0)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "summary_attestation_valid_consistent",
                bool(summary.get("attestation_valid", False))
                == bool(attestation_validation.get("attestation_valid", False)),
                (
                    f"pipeline={summary.get('attestation_valid', False)} "
                    f"attestation_validation={attestation_validation.get('attestation_valid', False)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "summary_attestation_validation_checks_consistent",
                int(summary.get("attestation_validation_checks_passed", 0))
                == int(attestation_validation.get("checks_passed", 0))
                and int(summary.get("attestation_validation_checks_total", 0))
                == int(attestation_validation.get("checks_total", 0)),
                (
                    f"pipeline={summary.get('attestation_validation_checks_passed', 0)}/"
                    f"{summary.get('attestation_validation_checks_total', 0)} "
                    f"attestation_validation={attestation_validation.get('checks_passed', 0)}/"
                    f"{attestation_validation.get('checks_total', 0)}"
                ),
            )
        )

        artifact_manifest = pipeline.get("artifact_manifest", [])
        expected_paths = [
            str(repro_pipeline_path),
            str(attestation_path),
            str(attestation_validation_path),
        ]
        observed_paths = [item.get("path", "") for item in artifact_manifest]

        checks.append(
            _make_check(
                "artifact_manifest_count_expected",
                len(artifact_manifest) == len(expected_paths),
                f"observed={len(artifact_manifest)} expected={len(expected_paths)}",
            )
        )
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
                    f"artifact_exists_consistent::{item.get('path', '')}",
                    bool(item.get("exists", False)) == exists,
                    f"pipeline={item.get('exists', False)} filesystem={exists}",
                )
            )
            if exists and bool(item.get("exists", False)):
                checks.append(
                    _make_check(
                        f"artifact_sha_consistent::{item.get('path', '')}",
                        item.get("sha256", "") == _sha256(path),
                        f"pipeline={item.get('sha256', '')} filesystem={_sha256(path)}",
                    )
                )
                checks.append(
                    _make_check(
                        f"artifact_size_consistent::{item.get('path', '')}",
                        int(item.get("size_bytes", -1)) == path.stat().st_size,
                        f"pipeline={item.get('size_bytes', -1)} filesystem={path.stat().st_size}",
                    )
                )

        expected_success = (
            all(bool(stage.get("success", False)) for stage in stage_results)
            and bool(repro_pipeline.get("pipeline_success", False))
            and attestation.get("attestation_status", "blocked") == "attested"
            and bool(attestation_validation.get("attestation_valid", False))
        )
        checks.append(
            _make_check(
                "pipeline_success_consistent",
                bool(pipeline.get("pipeline_success", False)) == expected_success,
                f"pipeline={pipeline.get('pipeline_success', False)} expected={expected_success}",
            )
        )

    failed = [item for item in checks if not item["passed"]]
    pipeline_valid = len(failed) == 0

    report = {
        "suite": "v1.1.1-sync-ops-release-attestation-validation-pipeline-validator",
        "pipeline_valid": pipeline_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.1.1 Sync Ops Release Attestation Validation Pipeline Validation",
        "",
        f"- Pipeline Valid: {report['pipeline_valid']}",
        f"- Checks Total: {report['checks_total']}",
        f"- Checks Passed: {report['checks_passed']}",
        f"- Checks Failed: {report['checks_failed']}",
        "",
        "## Checks",
        "",
    ]

    for check in report["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    if report["failed_checks"]:
        lines.extend(["", "## Failed Checks", ""])
        for name in report["failed_checks"]:
            lines.append(f"- {name}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate deterministic sync-ops release-attestation validation pipeline"
    )
    parser.add_argument(
        "--pipeline",
        default="testnet/launch/sync_ops_release_attestation_validation_pipeline.json",
    )
    parser.add_argument(
        "--repro-pipeline",
        default="testnet/launch/sync_ops_reproducibility_validation_pipeline.json",
    )
    parser.add_argument(
        "--attestation",
        default="testnet/launch/sync_ops_release_attestation.json",
    )
    parser.add_argument(
        "--attestation-validation",
        default="testnet/launch/sync_ops_release_attestation_validation.json",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_release_attestation_validation_pipeline_validation.json",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_release_attestation_validation_pipeline_validation.md",
    )
    args = parser.parse_args()

    report = validate_pipeline(
        pipeline_path=Path(args.pipeline),
        repro_pipeline_path=Path(args.repro_pipeline),
        attestation_path=Path(args.attestation),
        attestation_validation_path=Path(args.attestation_validation),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Pipeline Valid: {report['pipeline_valid']}")
    print(f"Checks Passed: {report['checks_passed']}/{report['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
