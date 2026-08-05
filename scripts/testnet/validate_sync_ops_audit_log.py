#!/usr/bin/env python3
"""Validate deterministic sync ops post-release audit log integrity and consistency."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_AUDIT_ARTIFACTS = [
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


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def validate_audit_log(
    release_gate_path: Path,
    audit_log_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    gate = _load_json(release_gate_path)
    audit = _load_json(audit_log_path)

    checks: list[dict] = []

    checks.append(_make_check("release_gate_present", bool(gate), f"path={release_gate_path}"))
    checks.append(_make_check("audit_log_present", bool(audit), f"path={audit_log_path}"))

    if gate and audit:
        entries = audit.get("entries", [])
        expected_labels = [label for label, _ in EXPECTED_AUDIT_ARTIFACTS]
        expected_paths = [path for _, path in EXPECTED_AUDIT_ARTIFACTS]
        observed_labels = [entry.get("label", "") for entry in entries]
        observed_paths = [entry.get("path", "") for entry in entries]

        checks.append(
            _make_check(
                "suite_name_expected",
                audit.get("suite", "") == "v1.0.1-sync-ops-audit-log",
                f"suite={audit.get('suite', '')}",
            )
        )
        checks.append(
            _make_check(
                "entries_count_consistent",
                int(audit.get("artifacts_expected", 0)) == len(entries),
                f"artifacts_expected={audit.get('artifacts_expected', 0)} entries={len(entries)}",
            )
        )
        checks.append(
            _make_check(
                "artifacts_expected_matches_contract",
                int(audit.get("artifacts_expected", 0)) == len(EXPECTED_AUDIT_ARTIFACTS),
                (
                    f"artifacts_expected={audit.get('artifacts_expected', 0)} "
                    f"contract={len(EXPECTED_AUDIT_ARTIFACTS)}"
                ),
            )
        )
        checks.append(
            _make_check(
                "entry_labels_match_contract",
                observed_labels == expected_labels,
                f"observed={observed_labels} expected={expected_labels}",
            )
        )
        checks.append(
            _make_check(
                "entry_paths_match_contract",
                observed_paths == expected_paths,
                f"observed={observed_paths} expected={expected_paths}",
            )
        )

        present_count = sum(1 for entry in entries if bool(entry.get("present", False)))
        missing_count = len(entries) - present_count

        checks.append(
            _make_check(
                "artifacts_present_count_consistent",
                int(audit.get("artifacts_present", -1)) == present_count,
                f"audit={audit.get('artifacts_present', -1)} computed={present_count}",
            )
        )
        checks.append(
            _make_check(
                "artifacts_missing_count_consistent",
                int(audit.get("artifacts_missing", -1)) == missing_count,
                f"audit={audit.get('artifacts_missing', -1)} computed={missing_count}",
            )
        )
        checks.append(
            _make_check(
                "audit_complete_consistent",
                bool(audit.get("audit_complete", False)) == (present_count == len(EXPECTED_AUDIT_ARTIFACTS)),
                f"audit_complete={audit.get('audit_complete', False)} present={present_count}/{len(EXPECTED_AUDIT_ARTIFACTS)}",
            )
        )

        checks.append(
            _make_check(
                "release_decision_consistent",
                audit.get("release_decision", "unknown") == gate.get("release_decision", "unknown"),
                f"audit={audit.get('release_decision', 'unknown')} gate={gate.get('release_decision', 'unknown')}",
            )
        )
        checks.append(
            _make_check(
                "certificate_fingerprint_consistent",
                audit.get("certificate_fingerprint", "") == gate.get("certificate_fingerprint", ""),
                (
                    f"audit={audit.get('certificate_fingerprint', '')} "
                    f"gate={gate.get('certificate_fingerprint', '')}"
                ),
            )
        )
        checks.append(
            _make_check(
                "assurance_score_consistent",
                int(audit.get("assurance_score", 0)) == int(gate.get("assurance_score", 0)),
                f"audit={audit.get('assurance_score', 0)} gate={gate.get('assurance_score', 0)}",
            )
        )
        checks.append(
            _make_check(
                "approval_mode_consistent",
                audit.get("approval_mode", "unknown") == gate.get("approval_mode", "unknown"),
                f"audit={audit.get('approval_mode', 'unknown')} gate={gate.get('approval_mode', 'unknown')}",
            )
        )

        required_entry_labels = {"release_gate", "release_certificate", "release_certificate_validation", "finalization_pipeline"}
        seen_labels: set[str] = set()

        for entry in entries:
            label = entry.get("label", "")
            seen_labels.add(label)
            path = Path(entry.get("path", ""))
            present = bool(entry.get("present", False))

            if path.exists() and present:
                computed_sha = _sha256(path)
                computed_size = path.stat().st_size
                checks.append(
                    _make_check(
                        f"entry_sha_matches::{label}",
                        entry.get("sha256", "") == computed_sha,
                        f"recorded={entry.get('sha256', '')} computed={computed_sha}",
                    )
                )
                checks.append(
                    _make_check(
                        f"entry_size_matches::{label}",
                        int(entry.get("size_bytes", 0)) == computed_size,
                        f"recorded={entry.get('size_bytes', 0)} computed={computed_size}",
                    )
                )
            elif not path.exists() and not present:
                checks.append(
                    _make_check(
                        f"entry_missing_shape_valid::{label}",
                        entry.get("sha256", "") == "" and int(entry.get("size_bytes", 0)) == 0,
                        f"sha={entry.get('sha256', '')} size={entry.get('size_bytes', 0)}",
                    )
                )
            else:
                checks.append(
                    _make_check(
                        f"entry_presence_flag_consistent::{label}",
                        False,
                        f"present={present} path_exists={path.exists()} path={path}",
                    )
                )

            key_fields = entry.get("key_fields", {})
            if label == "release_gate" and present:
                checks.append(
                    _make_check(
                        "release_gate_key_field_release_decision_consistent",
                        key_fields.get("release_decision", "unknown") == gate.get("release_decision", "unknown"),
                        f"entry={key_fields.get('release_decision', 'unknown')} gate={gate.get('release_decision', 'unknown')}",
                    )
                )
            if label == "release_certificate" and present:
                checks.append(
                    _make_check(
                        "release_certificate_key_field_fingerprint_consistent",
                        key_fields.get("certificate_fingerprint", "") == gate.get("certificate_fingerprint", ""),
                        (
                            f"entry={key_fields.get('certificate_fingerprint', '')} "
                            f"gate={gate.get('certificate_fingerprint', '')}"
                        ),
                    )
                )
            if label == "release_certificate_validation" and present:
                checks.append(
                    _make_check(
                        "release_certificate_validation_key_field_present",
                        "certificate_valid" in key_fields,
                        f"keys={sorted(key_fields.keys())}",
                    )
                )
            if label == "finalization_pipeline" and present:
                checks.append(
                    _make_check(
                        "finalization_pipeline_key_field_present",
                        "pipeline_success" in key_fields,
                        f"keys={sorted(key_fields.keys())}",
                    )
                )

        checks.append(
            _make_check(
                "required_entry_labels_present",
                required_entry_labels.issubset(seen_labels),
                f"missing={sorted(required_entry_labels.difference(seen_labels))}",
            )
        )

    failed = [item for item in checks if not item["passed"]]
    audit_valid = len(failed) == 0

    validation = {
        "suite": "v1.0.2-sync-ops-audit-validator",
        "audit_valid": audit_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.2 Sync Ops Audit Log Validation",
        "",
        f"- Audit Valid: {validation['audit_valid']}",
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
    parser = argparse.ArgumentParser(description="Validate deterministic sync ops post-release audit log")
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
        "--output-json",
        default="testnet/launch/sync_ops_audit_log_validation.json",
        help="Validation JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_audit_log_validation.md",
        help="Validation markdown output path",
    )
    args = parser.parse_args()

    validation = validate_audit_log(
        release_gate_path=Path(args.release_gate),
        audit_log_path=Path(args.audit_log),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Audit Valid: {validation['audit_valid']}")
    print(f"Checks Passed: {validation['checks_passed']}/{validation['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()