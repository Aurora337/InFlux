#!/usr/bin/env python3
"""Run deterministic sync operations assurance pipeline and emit a consolidated report."""

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
    tail = []
    stdout_lines = result.stdout.strip().splitlines() if result.stdout else []
    if stdout_lines:
        tail = stdout_lines[-4:]

    return {
        "step": step_id,
        "command": " ".join(command),
        "success": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout_tail": tail,
        "stderr_tail": (result.stderr.strip().splitlines()[-4:] if result.stderr else []),
    }


def run_pipeline(
    inject_failure_suite: str,
    inject_failure_attempt: int,
    min_readiness_score: int,
    output_json: Path,
    output_md: Path,
) -> dict:
    supervisor_cmd = ["/usr/bin/python3", "scripts/testnet/run_sync_orchestration_supervisor.py"]
    if inject_failure_suite:
        supervisor_cmd.extend(["--inject-failure-suite", inject_failure_suite])
    if inject_failure_attempt > 0:
        supervisor_cmd.extend(["--inject-failure-attempt", str(inject_failure_attempt)])

    steps = [
        ("supervisor", supervisor_cmd),
        ("runbook", ["/usr/bin/python3", "scripts/testnet/generate_sync_ops_runbook.py"]),
        ("handoff", ["/usr/bin/python3", "scripts/testnet/generate_sync_handoff_note.py"]),
        ("stability_gate", ["/usr/bin/python3", "scripts/testnet/validate_sync_ops_stability_gate.py"]),
        (
            "promotion_packet",
            [
                "/usr/bin/python3",
                "scripts/testnet/generate_sync_ops_promotion_packet.py",
                "--min-readiness-score",
                str(min_readiness_score),
            ],
        ),
        ("promotion_packet_validation", ["/usr/bin/python3", "scripts/testnet/validate_sync_ops_promotion_packet.py"]),
        ("assurance_report", ["/usr/bin/python3", "scripts/testnet/generate_sync_ops_assurance_report.py"]),
        ("assurance_report_validation", ["/usr/bin/python3", "scripts/testnet/validate_sync_ops_assurance_report.py"]),
    ]

    stage_results: list[dict] = []
    for step_id, command in steps:
        stage = _run_step(step_id=step_id, command=command)
        stage_results.append(stage)
        if not stage["success"]:
            break

    runbook_path = Path("testnet/launch/sync_ops_runbook.json")
    gate_path = Path("testnet/launch/sync_ops_stability_gate.json")
    packet_path = Path("testnet/launch/sync_ops_promotion_packet.json")
    packet_validation_path = Path("testnet/launch/sync_ops_promotion_packet_validation.json")
    assurance_path = Path("testnet/launch/sync_ops_assurance_report.json")
    assurance_validation_path = Path("testnet/launch/sync_ops_assurance_report_validation.json")

    gate = _load_json(gate_path)
    packet_validation = _load_json(packet_validation_path)
    assurance = _load_json(assurance_path)
    assurance_validation = _load_json(assurance_validation_path)

    pipeline_success = (
        all(item["success"] for item in stage_results)
        and bool(gate.get("gate_passed", False))
        and bool(packet_validation.get("packet_valid", False))
        and bool(assurance_validation.get("report_valid", False))
    )

    artifact_manifest = []
    for path in [runbook_path, gate_path, packet_path, packet_validation_path, assurance_path, assurance_validation_path]:
        if not path.exists():
            artifact_manifest.append({"path": str(path), "exists": False, "sha256": "", "size_bytes": 0})
            continue
        artifact_manifest.append(
            {
                "path": str(path),
                "exists": True,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )

    report = {
        "suite": "v0.9.2-sync-ops-assurance-pipeline",
        "pipeline_success": pipeline_success,
        "stages_total": len(steps),
        "stages_executed": len(stage_results),
        "stages_succeeded": sum(1 for item in stage_results if item["success"]),
        "failed_stage": next((item["step"] for item in stage_results if not item["success"]), "none"),
        "injected_failure": {
            "suite": inject_failure_suite or "none",
            "attempt": inject_failure_attempt,
        },
        "input_summary": {
            "gate_passed": bool(gate.get("gate_passed", False)),
            "packet_valid": bool(packet_validation.get("packet_valid", False)),
            "assurance_report_valid": bool(assurance_validation.get("report_valid", False)),
            "assurance_score": int(assurance.get("assurance_score", 0)),
            "assurance_level": assurance.get("assurance_level", "unknown"),
            "release_readiness": assurance.get("release_readiness", "unknown"),
        },
        "stage_results": stage_results,
        "artifact_manifest": artifact_manifest,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.2 Sync Ops Assurance Pipeline",
        "",
        f"- Pipeline Success: {report['pipeline_success']}",
        f"- Stages Executed: {report['stages_executed']}/{report['stages_total']}",
        f"- Stages Succeeded: {report['stages_succeeded']}",
        f"- Failed Stage: {report['failed_stage']}",
        f"- Injected Failure Suite: {report['injected_failure']['suite']}",
        f"- Injected Failure Attempt: {report['injected_failure']['attempt']}",
        "",
        "## Input Summary",
        "",
        f"- gate_passed={report['input_summary']['gate_passed']}",
        f"- packet_valid={report['input_summary']['packet_valid']}",
        f"- assurance_report_valid={report['input_summary']['assurance_report_valid']}",
        f"- assurance_score={report['input_summary']['assurance_score']}",
        f"- assurance_level={report['input_summary']['assurance_level']}",
        f"- release_readiness={report['input_summary']['release_readiness']}",
        "",
        "## Stage Results",
        "",
    ]

    for stage in report["stage_results"]:
        lines.append(
            f"- step={stage['step']} success={stage['success']} exit_code={stage['exit_code']} command={stage['command']}"
        )
        for out in stage["stdout_tail"]:
            lines.append(f"  - stdout: {out}")
        for err in stage["stderr_tail"]:
            lines.append(f"  - stderr: {err}")

    lines.extend(["", "## Artifact Manifest", ""])
    for artifact in report["artifact_manifest"]:
        lines.append(
            f"- path={artifact['path']} exists={artifact['exists']} size_bytes={artifact['size_bytes']} sha256={artifact['sha256']}"
        )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic sync ops assurance pipeline")
    parser.add_argument("--inject-failure-suite", default="", help="Optional suite id to force failure in supervisor attempt")
    parser.add_argument("--inject-failure-attempt", type=int, default=0, help="Attempt index for injected failure")
    parser.add_argument("--min-readiness-score", type=int, default=85, help="Minimum readiness score threshold for promotion packet")
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_assurance_pipeline.json",
        help="Pipeline JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_assurance_pipeline.md",
        help="Pipeline markdown output path",
    )
    args = parser.parse_args()

    report = run_pipeline(
        inject_failure_suite=args.inject_failure_suite,
        inject_failure_attempt=args.inject_failure_attempt,
        min_readiness_score=args.min_readiness_score,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Pipeline Success: {report['pipeline_success']}")
    print(f"Stages Succeeded: {report['stages_succeeded']}/{report['stages_total']}")
    print(f"Failed Stage: {report['failed_stage']}")
    print(f"Assurance Score: {report['input_summary']['assurance_score']}")
    print(f"Release Readiness: {report['input_summary']['release_readiness']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
