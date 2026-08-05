#!/usr/bin/env python3
"""Run deterministic cluster emergence simulation and validation pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: list[str]) -> dict:
    completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
    return {
        "command": " ".join(command),
        "success": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout.strip().splitlines()[-6:] if completed.stdout else [],
        "stderr_tail": completed.stderr.strip().splitlines()[-6:] if completed.stderr else [],
    }


def _render_markdown(report: dict) -> str:
    lines = [
        "# v1.3.7 Cluster Emergence Validation Pipeline",
        "",
        f"- pipeline_success: {report['pipeline_success']}",
        f"- replay_match: {report['summary']['replay_match']}",
        f"- validation_passed: {report['summary']['validation_passed']}",
        f"- checks_passed: {report['summary']['validation_checks_passed']}/{report['summary']['validation_checks_total']}",
        "",
        "## Stage Results",
        "",
    ]

    for stage in report["stage_results"]:
        lines.append(f"- {stage['stage']}: success={stage['success']} exit_code={stage['exit_code']}")

    return "\n".join(lines) + "\n"


def run_pipeline(output_json: Path, output_md: Path, events_input: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="influx_cluster_pipeline_") as temp_dir:
        temp_path = Path(temp_dir)
        run1_json = temp_path / "cluster_emergence_report_run1.json"
        run2_json = temp_path / "cluster_emergence_report_run2.json"
        run1_md = temp_path / "cluster_emergence_report_run1.md"
        run2_md = temp_path / "cluster_emergence_report_run2.md"
        validation_json = temp_path / "cluster_emergence_validation.json"
        validation_md = temp_path / "cluster_emergence_validation.md"

        extra_args = []
        if events_input:
            extra_args = ["--events-input", events_input]

        steps = [
            (
                "simulate_run_1",
                [
                    sys.executable,
                    "scripts/testnet/simulate_cluster_emergence.py",
                    *extra_args,
                    "--output",
                    str(run1_json),
                    "--markdown-output",
                    str(run1_md),
                ],
            ),
            (
                "simulate_run_2",
                [
                    sys.executable,
                    "scripts/testnet/simulate_cluster_emergence.py",
                    *extra_args,
                    "--output",
                    str(run2_json),
                    "--markdown-output",
                    str(run2_md),
                ],
            ),
            (
                "validate_report",
                [
                    sys.executable,
                    "scripts/testnet/validate_cluster_emergence.py",
                    "--input",
                    str(run2_json),
                    "--output",
                    str(validation_json),
                    "--markdown-output",
                    str(validation_md),
                ],
            ),
        ]

        stage_results = []
        for stage_name, command in steps:
            result = _run(command)
            result["stage"] = stage_name
            stage_results.append(result)
            if not result["success"]:
                break

        run1_hash = _sha256(run1_json) if run1_json.exists() else ""
        run2_hash = _sha256(run2_json) if run2_json.exists() else ""
        replay_match = bool(run1_hash and run2_hash and run1_hash == run2_hash)

        validation = {}
        if validation_json.exists():
            validation = json.loads(validation_json.read_text(encoding="utf-8"))

        validation_passed = bool(validation.get("report_valid", False))

        pipeline_success = all(stage["success"] for stage in stage_results) and replay_match and validation_passed

        report = {
            "suite": "v1.3.7-cluster-emergence-validation-pipeline",
            "pipeline_success": pipeline_success,
            "stage_results": stage_results,
            "summary": {
                "replay_match": replay_match,
                "run1_sha256": run1_hash,
                "run2_sha256": run2_hash,
                "validation_passed": validation_passed,
                "validation_checks_passed": int(validation.get("checks_passed", 0)),
                "validation_checks_total": int(validation.get("checks_total", 0)),
                "validation_failed_checks": validation.get("failed_checks", []),
            },
        }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic cluster emergence validation pipeline")
    parser.add_argument("--events-input", default="", help="Optional JSON array input for simulation events")
    parser.add_argument("--output-json", default="testnet/launch/cluster_emergence_pipeline.json")
    parser.add_argument("--output-md", default="testnet/launch/cluster_emergence_pipeline.md")
    args = parser.parse_args()

    output_json = Path(args.output_json)
    if not output_json.is_absolute():
        output_json = ROOT / output_json
    output_md = Path(args.output_md)
    if not output_md.is_absolute():
        output_md = ROOT / output_md

    report = run_pipeline(output_json=output_json, output_md=output_md, events_input=args.events_input)

    print(f"Pipeline success: {report['pipeline_success']}")
    print(f"Replay match: {report['summary']['replay_match']}")
    print(f"Validation passed: {report['summary']['validation_passed']}")
    print(
        "Validation checks: "
        f"{report['summary']['validation_checks_passed']}/"
        f"{report['summary']['validation_checks_total']}"
    )
    print(f"Output JSON: {output_json}")
    print(f"Output MD: {output_md}")
    return 0 if report["pipeline_success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
