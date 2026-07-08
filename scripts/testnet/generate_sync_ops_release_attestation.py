#!/usr/bin/env python3
"""Generate deterministic release attestation from reproducibility validation pipeline outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED_SIGNOFFS = [
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


def generate_attestation(
    pipeline_path: Path,
    manifest_path: Path,
    manifest_validation_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    pipeline = _load_json(pipeline_path)
    manifest = _load_json(manifest_path)
    manifest_validation = _load_json(manifest_validation_path)

    checks: list[dict] = []
    checks.append(_make_check("pipeline_present", bool(pipeline), f"path={pipeline_path}"))
    checks.append(_make_check("manifest_present", bool(manifest), f"path={manifest_path}"))
    checks.append(_make_check("manifest_validation_present", bool(manifest_validation), f"path={manifest_validation_path}"))

    if pipeline and manifest and manifest_validation:
        summary = pipeline.get("summary", {})
        terminal = manifest.get("terminal_summary", {})

        checks.append(
            _make_check(
                "pipeline_success",
                bool(pipeline.get("pipeline_success", False)),
                f"pipeline_success={pipeline.get('pipeline_success', False)}",
            )
        )
        checks.append(
            _make_check(
                "reproducible",
                bool(summary.get("reproducible", False)),
                f"reproducible={summary.get('reproducible', False)}",
            )
        )
        checks.append(
            _make_check(
                "manifest_valid",
                bool(summary.get("manifest_valid", False)) and bool(manifest_validation.get("manifest_valid", False)),
                (
                    f"pipeline_summary={summary.get('manifest_valid', False)} "
                    f"manifest_validation={manifest_validation.get('manifest_valid', False)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "no_mismatches",
                int(summary.get("mismatch_paths", 0)) == 0 and len(manifest.get("mismatch_paths", [])) == 0,
                (
                    f"pipeline_summary={summary.get('mismatch_paths', 0)} "
                    f"manifest={len(manifest.get('mismatch_paths', []))}"
                ),
            )
        )
        checks.append(
            _make_check(
                "audit_valid",
                bool(summary.get("audit_valid", False)) and bool(terminal.get("audit_valid", False)),
                f"pipeline={summary.get('audit_valid', False)} manifest_terminal={terminal.get('audit_valid', False)}",
            )
        )
        checks.append(
            _make_check(
                "release_decision_approved",
                summary.get("release_decision", "blocked") == "approved"
                and terminal.get("release_decision", "blocked") == "approved",
                (
                    f"pipeline={summary.get('release_decision', 'blocked')} "
                    f"manifest_terminal={terminal.get('release_decision', 'blocked')}"
                ),
            )
        )

    failed = [item for item in checks if not item["passed"]]
    attestation_status = "attested" if not failed else "blocked"

    pipeline_sha = _sha256(pipeline_path) if pipeline_path.exists() else ""
    manifest_sha = _sha256(manifest_path) if manifest_path.exists() else ""
    validation_sha = _sha256(manifest_validation_path) if manifest_validation_path.exists() else ""

    attestation_payload = {
        "status": attestation_status,
        "release_version": manifest.get("release_version", "unknown"),
        "pipeline_sha256": pipeline_sha,
        "manifest_sha256": manifest_sha,
        "manifest_validation_sha256": validation_sha,
        "required_signoffs": REQUIRED_SIGNOFFS,
        "failed_checks": [item["check"] for item in failed],
    }
    attestation_fingerprint = _sha256_text(json.dumps(attestation_payload, sort_keys=True))

    attestation = {
        "suite": "v1.0.9-sync-ops-release-attestation",
        "attestation_status": attestation_status,
        "attestation_fingerprint": attestation_fingerprint,
        "release_version": manifest.get("release_version", "unknown"),
        "release_decision": manifest.get("terminal_summary", {}).get("release_decision", "unknown"),
        "audit_valid": bool(manifest.get("terminal_summary", {}).get("audit_valid", False)),
        "reproducible": bool(manifest.get("reproducible", False)),
        "manifest_valid": bool(manifest_validation.get("manifest_valid", False)),
        "required_signoffs": REQUIRED_SIGNOFFS,
        "artifact_manifest": [
            {"path": str(pipeline_path), "sha256": pipeline_sha, "exists": pipeline_path.exists()},
            {"path": str(manifest_path), "sha256": manifest_sha, "exists": manifest_path.exists()},
            {"path": str(manifest_validation_path), "sha256": validation_sha, "exists": manifest_validation_path.exists()},
        ],
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(attestation, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.9 Sync Ops Release Attestation",
        "",
        f"- Attestation Status: {attestation['attestation_status']}",
        f"- Release Version: {attestation['release_version']}",
        f"- Release Decision: {attestation['release_decision']}",
        f"- Reproducible: {attestation['reproducible']}",
        f"- Manifest Valid: {attestation['manifest_valid']}",
        f"- Audit Valid: {attestation['audit_valid']}",
        f"- Attestation Fingerprint: {attestation['attestation_fingerprint']}",
        f"- Checks: {attestation['checks_passed']}/{attestation['checks_total']}",
        "",
        "## Required Sign-Offs",
        "",
    ]

    for signer in attestation["required_signoffs"]:
        lines.append(f"- {signer}")

    lines.extend(["", "## Artifact Manifest", ""])
    for artifact in attestation["artifact_manifest"]:
        lines.append(f"- path={artifact['path']} exists={artifact['exists']} sha256={artifact['sha256']}")

    lines.extend(["", "## Checks", ""])
    for check in attestation["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return attestation


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync-ops release attestation")
    parser.add_argument(
        "--pipeline",
        default="testnet/launch/sync_ops_reproducibility_validation_pipeline.json",
        help="Reproducibility validation pipeline JSON path",
    )
    parser.add_argument(
        "--manifest",
        default="testnet/launch/sync_ops_reproducibility_manifest.json",
        help="Reproducibility manifest JSON path",
    )
    parser.add_argument(
        "--manifest-validation",
        default="testnet/launch/sync_ops_reproducibility_manifest_validation.json",
        help="Reproducibility manifest validation JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_release_attestation.json",
        help="Attestation JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_release_attestation.md",
        help="Attestation markdown output path",
    )
    args = parser.parse_args()

    attestation = generate_attestation(
        pipeline_path=Path(args.pipeline),
        manifest_path=Path(args.manifest),
        manifest_validation_path=Path(args.manifest_validation),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Attestation Status: {attestation['attestation_status']}")
    print(f"Checks Passed: {attestation['checks_passed']}/{attestation['checks_total']}")
    print(f"Attestation Fingerprint: {attestation['attestation_fingerprint']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()