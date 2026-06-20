#!/usr/bin/env python3
"""Generate deterministic post-release audit log from all terminal sync ops pipeline artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


AUDIT_ARTIFACTS = [
    ("finalization_pipeline", "testnet/launch/sync_ops_finalization_pipeline.json"),
    ("release_gate", "testnet/launch/sync_ops_release_gate.json"),
    ("release_certificate", "testnet/launch/sync_ops_release_certificate.json"),
    ("release_certificate_validation", "testnet/launch/sync_ops_release_certificate_validation.json"),
    ("governance_pipeline", "testnet/launch/sync_ops_governance_pipeline.json"),
    ("governance_report", "testnet/launch/sync_ops_governance_report.json"),
    ("governance_report_validation", "testnet/launch/sync_ops_governance_report_validation.json"),
    ("assurance_pipeline", "testnet/launch/sync_ops_assurance_pipeline.json"),
    ("assurance_report", "testnet/launch/sync_ops_assurance_report.json"),
    ("assurance_report_validation", "testnet/launch/sync_ops_assurance_report_validation.json"),
    ("stability_gate", "testnet/launch/sync_ops_stability_gate.json"),
    ("promotion_packet", "testnet/launch/sync_ops_promotion_packet.json"),
    ("promotion_packet_validation", "testnet/launch/sync_ops_promotion_packet_validation.json"),
    ("sync_ops_runbook", "testnet/launch/sync_ops_runbook.json"),
    ("handoff_note", "testnet/launch/sync_ops_handoff_note.json"),
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


def _audit_entry(label: str, path: Path) -> dict:
    if not path.exists():
        return {
            "label": label,
            "path": str(path),
            "present": False,
            "sha256": "",
            "size_bytes": 0,
            "key_fields": {},
        }

    data = _load_json(path)
    key_fields: dict = {}

    if "release_decision" in data:
        key_fields["release_decision"] = data["release_decision"]
    if "certificate_status" in data:
        key_fields["certificate_status"] = data["certificate_status"]
    if "certificate_fingerprint" in data:
        key_fields["certificate_fingerprint"] = data["certificate_fingerprint"]
    if "certificate_valid" in data:
        key_fields["certificate_valid"] = data["certificate_valid"]
    if "pipeline_success" in data:
        key_fields["pipeline_success"] = data["pipeline_success"]
    if "gate_passed" in data:
        key_fields["gate_passed"] = data["gate_passed"]
    if "packet_valid" in data:
        key_fields["packet_valid"] = data["packet_valid"]
    if "report_valid" in data:
        key_fields["report_valid"] = data["report_valid"]
    if "assurance_score" in data:
        key_fields["assurance_score"] = data["assurance_score"]
    if "approval_mode" in data:
        key_fields["approval_mode"] = data["approval_mode"]
    if "operational_state" in data:
        key_fields["operational_state"] = data["operational_state"]

    return {
        "label": label,
        "path": str(path),
        "present": True,
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
        "key_fields": key_fields,
    }


def generate_audit_log(
    release_gate_path: Path,
    output_json: Path,
    output_md: Path,
    release_version: str,
) -> dict:
    gate = _load_json(release_gate_path)

    entries = []
    present_count = 0
    for label, rel_path in AUDIT_ARTIFACTS:
        entry = _audit_entry(label=label, path=Path(rel_path))
        entries.append(entry)
        if entry["present"]:
            present_count += 1

    audit_log = {
        "suite": "v1.0.1-sync-ops-audit-log",
        "release_version": release_version,
        "release_decision": gate.get("release_decision", "unknown"),
        "certificate_fingerprint": gate.get("certificate_fingerprint", ""),
        "assurance_score": int(gate.get("assurance_score", 0)),
        "approval_mode": gate.get("approval_mode", "unknown"),
        "artifacts_expected": len(AUDIT_ARTIFACTS),
        "artifacts_present": present_count,
        "artifacts_missing": len(AUDIT_ARTIFACTS) - present_count,
        "audit_complete": present_count == len(AUDIT_ARTIFACTS),
        "entries": entries,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(audit_log, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.1 Sync Ops Post-Release Audit Log",
        "",
        f"- Release Version: {audit_log['release_version']}",
        f"- Release Decision: {audit_log['release_decision']}",
        f"- Certificate Fingerprint: {audit_log['certificate_fingerprint']}",
        f"- Assurance Score: {audit_log['assurance_score']}",
        f"- Approval Mode: {audit_log['approval_mode']}",
        f"- Artifacts: {audit_log['artifacts_present']}/{audit_log['artifacts_expected']} present",
        f"- Audit Complete: {audit_log['audit_complete']}",
        "",
        "## Artifact Entries",
        "",
    ]

    for entry in audit_log["entries"]:
        lines.append(
            f"- label={entry['label']} present={entry['present']} size_bytes={entry['size_bytes']} sha256={entry['sha256']}"
        )
        for k, v in entry["key_fields"].items():
            lines.append(f"  - {k}={v}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return audit_log


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic post-release audit log")
    parser.add_argument(
        "--release-gate",
        default="testnet/launch/sync_ops_release_gate.json",
        help="Release gate JSON path",
    )
    parser.add_argument(
        "--release-version",
        default="1.0.0",
        help="Release version string",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_audit_log.json",
        help="Audit log JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_audit_log.md",
        help="Audit log markdown output path",
    )
    args = parser.parse_args()

    log = generate_audit_log(
        release_gate_path=Path(args.release_gate),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
        release_version=args.release_version,
    )

    print(f"Release Version: {log['release_version']}")
    print(f"Release Decision: {log['release_decision']}")
    print(f"Artifacts Present: {log['artifacts_present']}/{log['artifacts_expected']}")
    print(f"Audit Complete: {log['audit_complete']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
