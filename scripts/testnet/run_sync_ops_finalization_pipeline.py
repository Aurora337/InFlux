#!/usr/bin/env python3
"""Run full deterministic sync operations finalization pipeline ending with validated release certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from runtime_executable import python_cmd


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
    output_json: Path,
    output_md: Path,
) -> dict:
    supervisor_cmd = python_cmd("scripts/testnet/run_sync_orchestration_supervisor.py")
    if inject_failure_suite:
        supervisor_cmd.extend(["--inject-failure-suite", inject_failure_suite])
    if inject_failure_attempt > 0:
        supervisor_cmd.extend(["--inject-failure-attempt", str(inject_failure_attempt)])

    assurance_pipeline_cmd = python_cmd(
        "scripts/testnet/run_sync_ops_assurance_pipeline.py",
        "--min-readiness-score",
        str(min_readiness_score),
    )
    if inject_failure_suite:
        assurance_pipeline_cmd.extend(["--inject-failure-suite", inject_failure_suite])
    if inject_failure_attempt > 0:
        assurance_pipeline_cmd.extend(["--inject-failure-attempt", str(inject_failure_attempt)])

    steps = [
        ("supervisor", supervisor_cmd),
        ("runbook", python_cmd("scripts/testnet/generate_sync_ops_runbook.py")),
        ("handoff", python_cmd("scripts/testnet/generate_sync_handoff_note.py")),
        ("stability_gate", python_cmd("scripts/testnet/validate_sync_ops_stability_gate.py")),
        ("promotion_packet", python_cmd("scripts/testnet/generate_sync_ops_promotion_packet.py", "--min-readiness-score", str(min_readiness_score))),
        ("promotion_packet_validation", python_cmd("scripts/testnet/validate_sync_ops_promotion_packet.py")),
        ("assurance_report", python_cmd("scripts/testnet/generate_sync_ops_assurance_report.py")),
        ("assurance_report_validation", python_cmd("scripts/testnet/validate_sync_ops_assurance_report.py")),
        ("assurance_pipeline", assurance_pipeline_cmd),
        ("governance_report", python_cmd("scripts/testnet/generate_sync_ops_governance_report.py")),
        ("governance_report_validation", python_cmd("scripts/testnet/validate_sync_ops_governance_report.py")),
        ("governance_pipeline", python_cmd(
            "scripts/testnet/run_sync_ops_governance_pipeline.py",
            "--min-readiness-score",
            str(min_readiness_score),
        ) + (["--inject-failure-suite", inject_failure_suite] if inject_failure_suite else [])
          + (["--inject-failure-attempt", str(inject_failure_attempt)] if inject_failure_attempt > 0 else [])),
        ("release_certificate", python_cmd("scripts/testnet/generate_sync_ops_release_certificate.py")),
        ("release_certificate_validation", python_cmd("scripts/testnet/validate_sync_ops_release_certificate.py")),
    ]

    stage_results: list[dict] = []
    for step_id, command in steps:
        stage = _run_step(step_id=step_id, command=command)
        stage_results.append(stage)
        if not stage["success"]:
            break

    cert_path = Path("testnet/launch/sync_ops_release_certificate.json")
    cert_validation_path = Path("testnet/launch/sync_ops_release_certificate_validation.json")
    governance_pipeline_path = Path("testnet/launch/sync_ops_governance_pipeline.json")

    cert = _load_json(cert_path)
    cert_validation = _load_json(cert_validation_path)
    governance_pipeline = _load_json(governance_pipeline_path)

    pipeline_success = (
        all(s["success"] for s in stage_results)
        and bool(cert_validation.get("certificate_valid", False))
        and cert.get("certificate_status") in {"issued", "issued_conditional"}
    )

    terminal_paths = [cert_path, cert_validation_path, governance_pipeline_path]
    artifact_manifest = []
    for path in terminal_paths:
        if not path.exists():
            artifact_manifest.append({"path": str(path), "exists": False, "sha256": "", "size_bytes": 0})
        else:
            artifact_manifest.append({
                "path": str(path),
                "exists": True,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            })

    report = {
        "suite": "v0.9.6-sync-ops-finalization-pipeline",
        "pipeline_success": pipeline_success,
        "stages_total": len(steps),
        "stages_executed": len(stage_results),
        "stages_succeeded": sum(1 for s in stage_results if s["success"]),
        "failed_stage": next((s["step"] for s in stage_results if not s["success"]), "none"),
        "injected_failure": {
            "suite": inject_failure_suite or "none",
            "attempt": inject_failure_attempt,
        },
        "terminal_summary": {
            "certificate_status": cert.get("certificate_status", "unknown"),
            "certificate_fingerprint": cert.get("certificate_fingerprint", ""),
            "certificate_valid": bool(cert_validation.get("certificate_valid", False)),
            "approval_mode": governance_pipeline.get("input_summary", {}).get("approval_mode", "unknown"),
            "release_readiness": governance_pipeline.get("input_summary", {}).get("release_readiness", "unknown"),
            "assurance_score": int(governance_pipeline.get("input_summary", {}).get("assurance_score", 0)),
            "governance_blockers": governance_pipeline.get("input_summary", {}).get("governance_blockers", []),
            "required_signoffs": cert.get("required_signoffs", []),
        },
        "stage_results": stage_results,
        "artifact_manifest": artifact_manifest,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.6 Sync Ops Finalization Pipeline",
        "",
        f"- Pipeline Success: {report['pipeline_success']}",
        f"- Stages: {report['stages_succeeded']}/{report['stages_total']}",
        f"- Failed Stage: {report['failed_stage']}",
        "",
        "## Terminal Summary",
        "",
        f"- certificate_status={report['terminal_summary']['certificate_status']}",
        f"- certificate_fingerprint={report['terminal_summary']['certificate_fingerprint']}",
        f"- certificate_valid={report['terminal_summary']['certificate_valid']}",
        f"- approval_mode={report['terminal_summary']['approval_mode']}",
        f"- release_readiness={report['terminal_summary']['release_readiness']}",
        f"- assurance_score={report['terminal_summary']['assurance_score']}",
        f"- governance_blockers={report['terminal_summary']['governance_blockers']}",
        f"- required_signoffs={report['terminal_summary']['required_signoffs']}",
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
        lines.append(f"- path={artifact['path']} exists={artifact['exists']} size_bytes={artifact['size_bytes']} sha256={artifact['sha256']}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full deterministic sync ops finalization pipeline")
    parser.add_argument("--inject-failure-suite", default="", help="Suite id to force failure in supervisor attempt")
    parser.add_argument("--inject-failure-attempt", type=int, default=0, help="Attempt index for injected failure")
    parser.add_argument("--min-readiness-score", type=int, default=85, help="Minimum readiness score threshold")
    parser.add_argument("--output-json", default="testnet/launch/sync_ops_finalization_pipeline.json")
    parser.add_argument("--output-md", default="testnet/launch/sync_ops_finalization_pipeline.md")
    args = parser.parse_args()

    report = run_pipeline(
        inject_failure_suite=args.inject_failure_suite,
        inject_failure_attempt=args.inject_failure_attempt,
        min_readiness_score=args.min_readiness_score,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Pipeline Success: {report['pipeline_success']}")
    print(f"Stages: {report['stages_succeeded']}/{report['stages_total']}")
    print(f"Failed Stage: {report['failed_stage']}")
    print(f"Certificate Status: {report['terminal_summary']['certificate_status']}")
    print(f"Certificate Valid: {report['terminal_summary']['certificate_valid']}")
    print(f"Certificate Fingerprint: {report['terminal_summary']['certificate_fingerprint']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
