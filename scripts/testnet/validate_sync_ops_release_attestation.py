#!/usr/bin/env python3
"""Validate deterministic sync-ops release attestation integrity and consistency."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_SIGNOFFS = [
    "sync_oncall_lead",
    "release_manager",
    "audit_reviewer",
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


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def validate_attestation(
    attestation_path: Path,
    pipeline_path: Path,
    manifest_path: Path,
    manifest_validation_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    attestation = _load_json(attestation_path)
    pipeline = _load_json(pipeline_path)
    manifest = _load_json(manifest_path)
    manifest_validation = _load_json(manifest_validation_path)

    checks: list[dict] = []
    checks.append(_make_check("attestation_present", bool(attestation), f"path={attestation_path}"))
    checks.append(_make_check("pipeline_present", bool(pipeline), f"path={pipeline_path}"))
    checks.append(_make_check("manifest_present", bool(manifest), f"path={manifest_path}"))
    checks.append(
        _make_check("manifest_validation_present", bool(manifest_validation), f"path={manifest_validation_path}")
    )

    if attestation and pipeline and manifest and manifest_validation:
        checks.append(
            _make_check(
                "suite_name_expected",
                attestation.get("suite", "") == "v1.0.9-sync-ops-release-attestation",
                f"suite={attestation.get('suite', '')}",
            )
        )

        pipeline_summary = pipeline.get("summary", {})
        manifest_terminal = manifest.get("terminal_summary", {})

        expected_status = (
            "attested"
            if (
                bool(pipeline.get("pipeline_success", False))
                and bool(pipeline_summary.get("reproducible", False))
                and bool(pipeline_summary.get("manifest_valid", False))
                and int(pipeline_summary.get("mismatch_paths", 0)) == 0
                and bool(pipeline_summary.get("audit_valid", False))
                and pipeline_summary.get("release_decision", "blocked") == "approved"
                and bool(manifest_validation.get("manifest_valid", False))
            )
            else "blocked"
        )
        checks.append(
            _make_check(
                "attestation_status_consistent",
                attestation.get("attestation_status", "blocked") == expected_status,
                f"attestation={attestation.get('attestation_status', 'blocked')} expected={expected_status}",
            )
        )

        checks.append(
            _make_check(
                "release_version_consistent",
                attestation.get("release_version", "unknown") == manifest.get("release_version", "unknown"),
                f"attestation={attestation.get('release_version', 'unknown')} manifest={manifest.get('release_version', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "release_decision_consistent",
                attestation.get("release_decision", "unknown") == manifest_terminal.get("release_decision", "unknown"),
                f"attestation={attestation.get('release_decision', 'unknown')} manifest={manifest_terminal.get('release_decision', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "audit_valid_consistent",
                bool(attestation.get("audit_valid", False)) == bool(manifest_terminal.get("audit_valid", False)),
                f"attestation={attestation.get('audit_valid', False)} manifest={manifest_terminal.get('audit_valid', False)}",
            )
        )
        checks.append(
            _make_check(
                "reproducible_consistent",
                bool(attestation.get("reproducible", False)) == bool(manifest.get("reproducible", False)),
                f"attestation={attestation.get('reproducible', False)} manifest={manifest.get('reproducible', False)}",
            )
        )
        checks.append(
            _make_check(
                "manifest_valid_consistent",
                bool(attestation.get("manifest_valid", False)) == bool(manifest_validation.get("manifest_valid", False)),
                f"attestation={attestation.get('manifest_valid', False)} manifest_validation={manifest_validation.get('manifest_valid', False)}",
            )
        )

        checks.append(
            _make_check(
                "required_signoffs_expected",
                attestation.get("required_signoffs", []) == EXPECTED_SIGNOFFS,
                f"observed={attestation.get('required_signoffs', [])} expected={EXPECTED_SIGNOFFS}",
            )
        )

        artifact_manifest = attestation.get("artifact_manifest", [])
        checks.append(
            _make_check(
                "artifact_manifest_count_expected",
                len(artifact_manifest) == 3,
                f"manifest_count={len(artifact_manifest)} expected=3",
            )
        )

        expected_artifacts = [
            str(pipeline_path),
            str(manifest_path),
            str(manifest_validation_path),
        ]
        observed_artifacts = [item.get("path", "") for item in artifact_manifest]
        checks.append(
            _make_check(
                "artifact_manifest_paths_expected",
                observed_artifacts == expected_artifacts,
                f"observed={observed_artifacts} expected={expected_artifacts}",
            )
        )

        for item in artifact_manifest:
            path = Path(item.get("path", ""))
            exists = path.exists()
            checks.append(
                _make_check(
                    f"artifact_exists_consistent::{item.get('path', '')}",
                    bool(item.get("exists", False)) == exists,
                    f"attestation={item.get('exists', False)} filesystem={exists}",
                )
            )
            if exists and bool(item.get("exists", False)):
                checks.append(
                    _make_check(
                        f"artifact_sha_consistent::{item.get('path', '')}",
                        item.get("sha256", "") == _sha256(path),
                        f"attestation={item.get('sha256', '')} filesystem={_sha256(path)}",
                    )
                )

        failed_in_checks = [item for item in attestation.get("checks", []) if not item.get("passed", False)]
        checks.append(
            _make_check(
                "checks_total_consistent",
                int(attestation.get("checks_total", 0)) == len(attestation.get("checks", [])),
                f"attestation={attestation.get('checks_total', 0)} computed={len(attestation.get('checks', []))}",
            )
        )
        checks.append(
            _make_check(
                "checks_failed_consistent",
                int(attestation.get("checks_failed", 0)) == len(failed_in_checks),
                f"attestation={attestation.get('checks_failed', 0)} computed={len(failed_in_checks)}",
            )
        )
        checks.append(
            _make_check(
                "checks_passed_consistent",
                int(attestation.get("checks_passed", 0)) == (len(attestation.get("checks", [])) - len(failed_in_checks)),
                f"attestation={attestation.get('checks_passed', 0)} computed={len(attestation.get('checks', [])) - len(failed_in_checks)}",
            )
        )

        expected_failed_names = [item.get("check", "") for item in failed_in_checks]
        checks.append(
            _make_check(
                "failed_checks_list_consistent",
                sorted(attestation.get("failed_checks", [])) == sorted(expected_failed_names),
                f"attestation={sorted(attestation.get('failed_checks', []))} computed={sorted(expected_failed_names)}",
            )
        )

        payload = {
            "status": attestation.get("attestation_status", "blocked"),
            "release_version": attestation.get("release_version", "unknown"),
            "pipeline_sha256": attestation.get("artifact_manifest", [{}])[0].get("sha256", "") if attestation.get("artifact_manifest") else "",
            "manifest_sha256": attestation.get("artifact_manifest", [{}, {}])[1].get("sha256", "") if len(attestation.get("artifact_manifest", [])) > 1 else "",
            "manifest_validation_sha256": attestation.get("artifact_manifest", [{}, {}, {}])[2].get("sha256", "") if len(attestation.get("artifact_manifest", [])) > 2 else "",
            "required_signoffs": attestation.get("required_signoffs", []),
            "failed_checks": attestation.get("failed_checks", []),
        }
        expected_fingerprint = _sha256_text(json.dumps(payload, sort_keys=True))
        checks.append(
            _make_check(
                "attestation_fingerprint_consistent",
                attestation.get("attestation_fingerprint", "") == expected_fingerprint,
                f"attestation={attestation.get('attestation_fingerprint', '')} expected={expected_fingerprint}",
            )
        )

    failed = [item for item in checks if not item["passed"]]
    attestation_valid = len(failed) == 0

    validation = {
        "suite": "v1.0.9-sync-ops-release-attestation-validator",
        "attestation_valid": attestation_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.9 Sync Ops Release Attestation Validation",
        "",
        f"- Attestation Valid: {validation['attestation_valid']}",
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
    parser = argparse.ArgumentParser(description="Validate deterministic sync-ops release attestation")
    parser.add_argument("--attestation", default="testnet/launch/sync_ops_release_attestation.json")
    parser.add_argument("--pipeline", default="testnet/launch/sync_ops_reproducibility_validation_pipeline.json")
    parser.add_argument("--manifest", default="testnet/launch/sync_ops_reproducibility_manifest.json")
    parser.add_argument(
        "--manifest-validation",
        default="testnet/launch/sync_ops_reproducibility_manifest_validation.json",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_release_attestation_validation.json",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_release_attestation_validation.md",
    )
    args = parser.parse_args()

    validation = validate_attestation(
        attestation_path=Path(args.attestation),
        pipeline_path=Path(args.pipeline),
        manifest_path=Path(args.manifest),
        manifest_validation_path=Path(args.manifest_validation),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Attestation Valid: {validation['attestation_valid']}")
    print(f"Checks Passed: {validation['checks_passed']}/{validation['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()