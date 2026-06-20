#!/usr/bin/env python3
"""Validate deterministic sync operations release certificate integrity and fingerprint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


KNOWN_CERT_STATUSES = {"issued", "issued_conditional", "rejected"}


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def _expected_cert_status(pipeline_success: bool, approval_mode: str, governance_blockers: list[str]) -> str:
    if not pipeline_success or governance_blockers:
        return "rejected"
    if approval_mode == "approved":
        return "issued"
    if approval_mode == "conditional":
        return "issued_conditional"
    return "rejected"


def validate_release_certificate(
    governance_pipeline_path: Path,
    certificate_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    pipeline = _load_json(governance_pipeline_path)
    cert = _load_json(certificate_path)

    checks: list[dict] = []

    checks.append(_make_check("governance_pipeline_present", bool(pipeline), f"path={governance_pipeline_path}"))
    checks.append(_make_check("certificate_present", bool(cert), f"path={certificate_path}"))

    if pipeline and cert:
        # Status validity
        checks.append(
            _make_check(
                "certificate_status_valid",
                cert.get("certificate_status", "unknown") in KNOWN_CERT_STATUSES,
                f"status={cert.get('certificate_status', 'unknown')}",
            )
        )

        # Status consistency with inputs
        expected_status = _expected_cert_status(
            pipeline_success=bool(cert.get("pipeline_success", False)),
            approval_mode=cert.get("approval_mode", "blocked"),
            governance_blockers=cert.get("governance_blockers", []),
        )
        checks.append(
            _make_check(
                "certificate_status_consistent",
                cert.get("certificate_status", "unknown") == expected_status,
                f"cert={cert.get('certificate_status', 'unknown')} expected={expected_status}",
            )
        )

        # Fingerprint verification — recompute from cert fields (excluding fingerprint itself)
        cert_fields = {k: v for k, v in cert.items() if k != "certificate_fingerprint"}
        cert_body = json.dumps(cert_fields, sort_keys=True)
        recomputed_fingerprint = _sha256_text(cert_body)
        checks.append(
            _make_check(
                "certificate_fingerprint_valid",
                cert.get("certificate_fingerprint", "") == recomputed_fingerprint,
                f"recorded={cert.get('certificate_fingerprint', '')} recomputed={recomputed_fingerprint}",
            )
        )

        # Cross-check against governance pipeline
        pipeline_summary = pipeline.get("input_summary", {})
        checks.append(
            _make_check(
                "approval_mode_consistent",
                cert.get("approval_mode", "unknown") == pipeline_summary.get("approval_mode", "unknown"),
                f"cert={cert.get('approval_mode', 'unknown')} pipeline={pipeline_summary.get('approval_mode', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "release_readiness_consistent",
                cert.get("release_readiness", "unknown") == pipeline_summary.get("release_readiness", "unknown"),
                f"cert={cert.get('release_readiness', 'unknown')} pipeline={pipeline_summary.get('release_readiness', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "assurance_score_consistent",
                int(cert.get("assurance_score", 0)) == int(pipeline_summary.get("assurance_score", 0)),
                f"cert={cert.get('assurance_score', 0)} pipeline={pipeline_summary.get('assurance_score', 0)}",
            )
        )
        checks.append(
            _make_check(
                "pipeline_success_consistent",
                bool(cert.get("pipeline_success", False)) == bool(pipeline.get("pipeline_success", False)),
                f"cert={cert.get('pipeline_success', False)} pipeline={pipeline.get('pipeline_success', False)}",
            )
        )
        checks.append(
            _make_check(
                "stages_consistent",
                int(cert.get("stages_succeeded", 0)) == int(pipeline.get("stages_succeeded", 0))
                and int(cert.get("stages_total", 0)) == int(pipeline.get("stages_total", 0)),
                f"cert={cert.get('stages_succeeded', 0)}/{cert.get('stages_total', 0)} "
                f"pipeline={pipeline.get('stages_succeeded', 0)}/{pipeline.get('stages_total', 0)}",
            )
        )
        checks.append(
            _make_check(
                "governance_blockers_consistent",
                cert.get("governance_blockers", []) == pipeline_summary.get("governance_blockers", []),
                f"cert={cert.get('governance_blockers', [])} pipeline={pipeline_summary.get('governance_blockers', [])}",
            )
        )
        checks.append(
            _make_check(
                "required_signoffs_consistent",
                cert.get("required_signoffs", []) == pipeline_summary.get("required_signoffs", []),
                f"cert={cert.get('required_signoffs', [])} pipeline={pipeline_summary.get('required_signoffs', [])}",
            )
        )

        # Conditions only present when status is issued_conditional
        if cert.get("certificate_status") == "issued_conditional":
            checks.append(
                _make_check(
                    "conditions_non_empty_for_conditional",
                    len(cert.get("conditions", [])) > 0,
                    f"conditions_count={len(cert.get('conditions', []))}",
                )
            )
        else:
            checks.append(
                _make_check(
                    "conditions_empty_for_non_conditional",
                    len(cert.get("conditions", [])) == 0,
                    f"conditions_count={len(cert.get('conditions', []))}",
                )
            )

    failed = [item for item in checks if not item["passed"]]
    certificate_valid = len(failed) == 0

    validation = {
        "suite": "v0.9.5-sync-ops-release-certificate-validator",
        "certificate_valid": certificate_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.5 Sync Ops Release Certificate Validation",
        "",
        f"- Certificate Valid: {validation['certificate_valid']}",
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
    parser = argparse.ArgumentParser(description="Validate deterministic sync ops release certificate")
    parser.add_argument(
        "--governance-pipeline",
        default="testnet/launch/sync_ops_governance_pipeline.json",
        help="Governance pipeline JSON path",
    )
    parser.add_argument(
        "--certificate",
        default="testnet/launch/sync_ops_release_certificate.json",
        help="Release certificate JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_release_certificate_validation.json",
        help="Validation JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_release_certificate_validation.md",
        help="Validation markdown output path",
    )
    args = parser.parse_args()

    validation = validate_release_certificate(
        governance_pipeline_path=Path(args.governance_pipeline),
        certificate_path=Path(args.certificate),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Certificate Valid: {validation['certificate_valid']}")
    print(f"Checks Passed: {validation['checks_passed']}/{validation['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
