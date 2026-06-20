#!/usr/bin/env python3
"""Run deterministic sync ops audit assurance pipeline and validator in one command."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


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


def _run_step(step_id: str, command: list[str]) -> dict:
    result = subprocess.run(command, capture_output=True, text=True)
    stdout_lines = result.stdout.strip().splitlines() if result.stdout else []
    return {
        "step": step_id,
        "command": " ".join(command),
        "success": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout_tail": stdout_lines[-4:] if stdout_lines else [],
        "stderr_tail": result.stderr.strip().splitlines()[-4:] if result.stderr else [],
    }


def run_pipeline(
    inject_failure_suite: str,
    inject_failure_attempt: int,
    min_readiness_score: int,
    release_version: str,
    output_json: Path,
    output_md: Path,
) -> dict:
    audit_assurance_cmd = [
        "/usr/bin/python3",
        "scripts/testnet/run_sync_ops_audit_assurance_pipeline.py",
        "--min-readiness-score",
        str(min_readiness_score),
        "--release-version",
        release_version,
    ]
    if inject_failure_suite:
        audit_assurance_cmd.extend(["--inject-failure-suite", inject_failure_suite])
    if inject_failure_attempt > 0:
        audit_assurance_cmd.extend(["--inject-failure-attempt", str(inject_failure_attempt)])

    steps = [
        ("audit_assurance_pipeline", audit_assurance_cmd),
        (
            "audit_assurance_pipeline_validation",
            ["/usr/bin/python3", "scripts/testnet/validate_sync_ops_audit_assurance_pipeline.py"],
        ),
    ]

    stage_results: list[dict] = []
    for step_id, command in steps:
        stage = _run_step(step_id=step_id, command=command)
        stage_results.append(stage)
        if not stage["success"]:
            break

    audit_assurance = _load_json(Path("testnet/launch/sync_ops_audit_assurance_pipeline.json"))
    audit_assurance_validation = _load_json(Path("testnet/launch/sync_ops_audit_assurance_pipeline_validation.json"))

    summary = audit_assurance.get("summary", {})

    pipeline_success = (
        all(s["success"] for s in stage_results)
        and bool(audit_assurance.get("pipeline_success", False))
        and bool(audit_assurance_validation.get("pipeline_valid", False))
    )

    artifacts = [
        Path("testnet/launch/sync_ops_audit_assurance_pipeline.json"),
        Path("testnet/launch/sync_ops_audit_assurance_pipeline_validation.json"),
    ]
    artifact_manifest = []
    for path in artifacts:
        if not path.exists():
            artifact_manifest.append({"path": str(path), "exists": False, "sha256": "", "size_bytes": 0})
        else:
            artifact_manifest.append(
                {
                    "path": str(path),
                    "exists": True,
                    "sha256": _sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    report = {
        "suite": "v1.0.5-sync-ops-audit-assurance-validation-pipeline",
        "pipeline_success": pipeline_success,
        "stages_total": len(steps),
        "stages_executed": len(stage_results),
        "stages_succeeded": sum(1 for s in stage_results if s["success"]),
        "failed_stage": next((s["step"] for s in stage_results if not s["success"]), "none"),
        "injected_failure": {
            "suite": inject_failure_suite or "none",
            "attempt": inject_failure_attempt,
        },
        "summary": {
            "release_version": summary.get("release_version", release_version),
            "release_decision": summary.get("release_decision", "unknown"),
            "certificate_status": summary.get("certificate_status", "unknown"),
            "certificate_valid": bool(summary.get("certificate_valid", False)),
            "certificate_fingerprint": summary.get("certificate_fingerprint", ""),
            "assurance_score": int(summary.get("assurance_score", 0)),
            "approval_mode": summary.get("approval_mode", "unknown"),
            "audit_complete": bool(summary.get("audit_complete", False)),
            "audit_valid": bool(summary.get("audit_valid", False)),
            "audit_checks_passed": int(summary.get("audit_checks_passed", 0)),
            "audit_checks_total": int(summary.get("audit_checks_total", 0)),
            "pipeline_validation_valid": bool(audit_assurance_validation.get("pipeline_valid", False)),
            "pipeline_validation_checks_passed": int(audit_assurance_validation.get("checks_passed", 0)),
            "pipeline_validation_checks_total": int(audit_assurance_validation.get("checks_total", 0)),
        },
        "stage_results": stage_results,
        "artifact_manifest": artifact_manifest,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.5 Sync Ops Audit Assurance Validation Pipeline",
        "",
        f"- Pipeline Success: {report['pipeline_success']}",
        f"- Stages: {report['stages_succeeded']}/{report['stages_total']}",
        f"- Failed Stage: {report['failed_stage']}",
        "",
        "## Summary",
        "",
        f"- release_version={report['summary']['release_version']}",
        f"- release_decision={report['summary']['release_decision']}",
        f"- certificate_status={report['summary']['certificate_status']}",
        f"- certificate_valid={report['summary']['certificate_valid']}",
        f"- certificate_fingerprint={report['summary']['certificate_fingerprint']}",
        f"- assurance_score={report['summary']['assurance_score']}",
        f"- approval_mode={report['summary']['approval_mode']}",
        f"- audit_complete={report['summary']['audit_complete']}",
        f"- audit_valid={report['summary']['audit_valid']}",
        (
            f"- audit_checks={report['summary']['audit_checks_passed']}/"
            f"{report['summary']['audit_checks_total']}"
        ),
        f"- pipeline_validation_valid={report['summary']['pipeline_validation_valid']}",
        (
            f"- pipeline_validation_checks={report['summary']['pipeline_validation_checks_passed']}/"
            f"{report['summary']['pipeline_validation_checks_total']}"
        ),
        "",
        "## Stage Results",
        "",
    ]

    for stage in report["stage_results"]:
        lines.append(f"- step={stage['step']} success={stage['success']} exit_code={stage['exit_code']}")
        for out in stage["stdout_tail"]:
            lines.append(f"  - stdout: {out}")

    lines.extend(["", "## Artifact Manifest", ""])
    for artifact in report["artifact_manifest"]:
        lines.append(
            f"- path={artifact['path']} exists={artifact['exists']} size_bytes={artifact['size_bytes']} sha256={artifact['sha256']}"
        )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic sync ops audit assurance validation pipeline")
    parser.add_argument("--inject-failure-suite", default="", help="Suite id to force failure in supervisor attempt")
    parser.add_argument("--inject-failure-attempt", type=int, default=0, help="Attempt index for injected failure")
    parser.add_argument("--min-readiness-score", type=int, default=85, help="Minimum readiness score threshold")
    parser.add_argument("--release-version", default="1.0.4", help="Release version string for audit log")
    parser.add_argument("--output-json", default="testnet/launch/sync_ops_audit_assurance_validation_pipeline.json")
    parser.add_argument("--output-md", default="testnet/launch/sync_ops_audit_assurance_validation_pipeline.md")
    args = parser.parse_args()

    report = run_pipeline(
        inject_failure_suite=args.inject_failure_suite,
        inject_failure_attempt=args.inject_failure_attempt,
        min_readiness_score=args.min_readiness_score,
        release_version=args.release_version,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Pipeline Success: {report['pipeline_success']}")
    print(f"Stages: {report['stages_succeeded']}/{report['stages_total']}")
    print(f"Failed Stage: {report['failed_stage']}")
    print(f"Release Decision: {report['summary']['release_decision']}")
    print(f"Audit Valid: {report['summary']['audit_valid']}")
    print(
        f"Audit Checks: {report['summary']['audit_checks_passed']}/"
        f"{report['summary']['audit_checks_total']}"
    )
    print(f"Pipeline Validation Valid: {report['summary']['pipeline_validation_valid']}")
    print(
        f"Pipeline Validation Checks: {report['summary']['pipeline_validation_checks_passed']}/"
        f"{report['summary']['pipeline_validation_checks_total']}"
    )
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()