#!/usr/bin/env python3
"""Generate deterministic v1.0.0 release readiness gate from finalization pipeline output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_CERT_STATUSES = {"issued", "issued_conditional"}
MINIMUM_ASSURANCE_SCORE = 75


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def _release_decision(checks: list[dict], release_blockers: list[str]) -> str:
    failed = [item for item in checks if not item["passed"]]
    if failed or release_blockers:
        return "blocked"
    return "approved"


def generate_release_gate(
    finalization_pipeline_path: Path,
    output_json: Path,
    output_md: Path,
    min_assurance_score: int,
) -> dict:
    pipeline = _load_json(finalization_pipeline_path)

    checks: list[dict] = []

    checks.append(
        _make_check(
            "finalization_pipeline_present",
            bool(pipeline),
            f"path={finalization_pipeline_path}",
        )
    )

    if pipeline:
        terminal = pipeline.get("terminal_summary", {})
        cert_status = terminal.get("certificate_status", "unknown")
        cert_valid = bool(terminal.get("certificate_valid", False))
        assurance_score = int(terminal.get("assurance_score", 0))
        approval_mode = terminal.get("approval_mode", "blocked")
        governance_blockers = list(terminal.get("governance_blockers", []))

        checks.append(
            _make_check(
                "pipeline_success",
                bool(pipeline.get("pipeline_success", False)),
                f"pipeline_success={pipeline.get('pipeline_success', False)}",
            )
        )
        checks.append(
            _make_check(
                "all_stages_succeeded",
                int(pipeline.get("stages_succeeded", 0)) == int(pipeline.get("stages_total", 0)),
                f"stages={pipeline.get('stages_succeeded', 0)}/{pipeline.get('stages_total', 0)}",
            )
        )
        checks.append(
            _make_check(
                "certificate_status_acceptable",
                cert_status in REQUIRED_CERT_STATUSES,
                f"certificate_status={cert_status} acceptable={sorted(REQUIRED_CERT_STATUSES)}",
            )
        )
        checks.append(
            _make_check(
                "certificate_valid",
                cert_valid,
                f"certificate_valid={cert_valid}",
            )
        )
        checks.append(
            _make_check(
                "assurance_score_threshold",
                assurance_score >= min_assurance_score,
                f"assurance_score={assurance_score} threshold={min_assurance_score}",
            )
        )
        checks.append(
            _make_check(
                "approval_mode_acceptable",
                approval_mode in {"approved", "conditional"},
                f"approval_mode={approval_mode}",
            )
        )
        checks.append(
            _make_check(
                "no_governance_blockers",
                len(governance_blockers) == 0,
                f"governance_blockers={governance_blockers}",
            )
        )

    failed_checks = [item for item in checks if not item["passed"]]

    release_blockers: list[str] = [item["check"] for item in failed_checks]
    terminal = pipeline.get("terminal_summary", {}) if pipeline else {}

    decision = _release_decision(checks=checks, release_blockers=release_blockers)

    conditions: list[str] = []
    if decision == "approved" and terminal.get("certificate_status") == "issued_conditional":
        conditions = [
            "Heightened monitoring required during first post-release sync cycle.",
            "Checkpoint review required after initial validator recovery pass.",
            "All finalization artifacts must be archived with the v1.0.0 release notes.",
        ]

    gate = {
        "suite": "v1.0.0-sync-ops-release-gate",
        "release_version": "1.0.0",
        "release_decision": decision,
        "certificate_status": terminal.get("certificate_status", "unknown"),
        "certificate_fingerprint": terminal.get("certificate_fingerprint", ""),
        "certificate_valid": bool(terminal.get("certificate_valid", False)),
        "assurance_score": int(terminal.get("assurance_score", 0)),
        "approval_mode": terminal.get("approval_mode", "unknown"),
        "release_readiness": terminal.get("release_readiness", "unknown"),
        "required_signoffs": terminal.get("required_signoffs", []),
        "governance_blockers": terminal.get("governance_blockers", []),
        "release_blockers": release_blockers,
        "conditions": conditions,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed_checks),
        "checks_failed": len(failed_checks),
        "failed_checks": [item["check"] for item in failed_checks],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.0 Sync Ops Release Gate",
        "",
        f"- Release Decision: {gate['release_decision']}",
        f"- Release Version: {gate['release_version']}",
        f"- Certificate Status: {gate['certificate_status']}",
        f"- Certificate Valid: {gate['certificate_valid']}",
        f"- Certificate Fingerprint: {gate['certificate_fingerprint']}",
        f"- Assurance Score: {gate['assurance_score']}",
        f"- Approval Mode: {gate['approval_mode']}",
        f"- Release Readiness: {gate['release_readiness']}",
        f"- Checks: {gate['checks_passed']}/{gate['checks_total']}",
        "",
        "## Release Blockers",
        "",
    ]

    if gate["release_blockers"]:
        for b in gate["release_blockers"]:
            lines.append(f"- {b}")
    else:
        lines.append("- none")

    lines.extend(["", "## Required Sign-Offs", ""])
    for s in gate["required_signoffs"]:
        lines.append(f"- {s}")

    if gate["conditions"]:
        lines.extend(["", "## Conditions", ""])
        for c in gate["conditions"]:
            lines.append(f"- {c}")

    lines.extend(["", "## Checks", ""])
    for check in gate["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return gate


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic v1.0.0 sync ops release gate")
    parser.add_argument(
        "--finalization-pipeline",
        default="testnet/launch/sync_ops_finalization_pipeline.json",
        help="Finalization pipeline JSON path",
    )
    parser.add_argument(
        "--min-assurance-score",
        type=int,
        default=MINIMUM_ASSURANCE_SCORE,
        help=f"Minimum assurance score for release approval (default {MINIMUM_ASSURANCE_SCORE})",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_release_gate.json",
        help="Release gate JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_release_gate.md",
        help="Release gate markdown output path",
    )
    args = parser.parse_args()

    gate = generate_release_gate(
        finalization_pipeline_path=Path(args.finalization_pipeline),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
        min_assurance_score=args.min_assurance_score,
    )

    print(f"Release Decision: {gate['release_decision']}")
    print(f"Certificate Status: {gate['certificate_status']}")
    print(f"Assurance Score: {gate['assurance_score']}")
    print(f"Checks Passed: {gate['checks_passed']}/{gate['checks_total']}")
    print(f"Release Blockers: {len(gate['release_blockers'])}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
