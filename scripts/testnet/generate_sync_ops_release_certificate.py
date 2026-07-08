#!/usr/bin/env python3
"""Generate deterministic sync operations release certificate from governance pipeline output."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _certificate_status(pipeline_success: bool, approval_mode: str, governance_blockers: list[str]) -> str:
    if not pipeline_success or governance_blockers:
        return "rejected"
    if approval_mode == "approved":
        return "issued"
    if approval_mode == "conditional":
        return "issued_conditional"
    return "rejected"


def generate_release_certificate(
    governance_pipeline_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    pipeline = _load_json(governance_pipeline_path)

    summary = pipeline.get("input_summary", {})
    approval_mode = summary.get("approval_mode", "blocked")
    release_readiness = summary.get("release_readiness", "not_ready")
    assurance_score = int(summary.get("assurance_score", 0))
    governance_blockers = list(summary.get("governance_blockers", []))
    governance_validation_passed = bool(summary.get("governance_validation_passed", False))
    required_signoffs = list(summary.get("required_signoffs", []))
    pipeline_success = bool(pipeline.get("pipeline_success", False))
    stages_succeeded = int(pipeline.get("stages_succeeded", 0))
    stages_total = int(pipeline.get("stages_total", 0))

    cert_status = _certificate_status(
        pipeline_success=pipeline_success,
        approval_mode=approval_mode,
        governance_blockers=governance_blockers,
    )

    conditions: list[str] = []
    if cert_status == "issued_conditional":
        conditions = [
            "Heightened monitoring required during first post-release sync cycle.",
            "Checkpoint review required after initial validator recovery pass.",
            "Assurance artifacts must be retained and attached to release notes.",
        ]

    cert_fields = {
        "suite": "v0.9.4-sync-ops-release-certificate",
        "certificate_status": cert_status,
        "approval_mode": approval_mode,
        "release_readiness": release_readiness,
        "assurance_score": assurance_score,
        "pipeline_success": pipeline_success,
        "stages_succeeded": stages_succeeded,
        "stages_total": stages_total,
        "governance_validation_passed": governance_validation_passed,
        "governance_blockers": governance_blockers,
        "required_signoffs": required_signoffs,
        "conditions": conditions,
    }

    cert_body = json.dumps(cert_fields, sort_keys=True)
    cert_fingerprint = _sha256_text(cert_body)

    certificate = {
        **cert_fields,
        "certificate_fingerprint": cert_fingerprint,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.4 Sync Ops Release Certificate",
        "",
        f"- Certificate Status: {certificate['certificate_status']}",
        f"- Certificate Fingerprint: {certificate['certificate_fingerprint']}",
        f"- Approval Mode: {certificate['approval_mode']}",
        f"- Release Readiness: {certificate['release_readiness']}",
        f"- Assurance Score: {certificate['assurance_score']}",
        f"- Pipeline Success: {certificate['pipeline_success']}",
        f"- Stages: {certificate['stages_succeeded']}/{certificate['stages_total']}",
        f"- Governance Validation Passed: {certificate['governance_validation_passed']}",
        "",
        "## Governance Blockers",
        "",
    ]

    if certificate["governance_blockers"]:
        for b in certificate["governance_blockers"]:
            lines.append(f"- {b}")
    else:
        lines.append("- none")

    lines.extend(["", "## Required Sign-Offs", ""])
    for s in certificate["required_signoffs"]:
        lines.append(f"- {s}")

    if certificate["conditions"]:
        lines.extend(["", "## Conditions", ""])
        for c in certificate["conditions"]:
            lines.append(f"- {c}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync ops release certificate")
    parser.add_argument(
        "--governance-pipeline",
        default="testnet/launch/sync_ops_governance_pipeline.json",
        help="Governance pipeline JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_release_certificate.json",
        help="Release certificate JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_release_certificate.md",
        help="Release certificate markdown output path",
    )
    args = parser.parse_args()

    cert = generate_release_certificate(
        governance_pipeline_path=Path(args.governance_pipeline),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Certificate Status: {cert['certificate_status']}")
    print(f"Certificate Fingerprint: {cert['certificate_fingerprint']}")
    print(f"Approval Mode: {cert['approval_mode']}")
    print(f"Blockers: {len(cert['governance_blockers'])}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
