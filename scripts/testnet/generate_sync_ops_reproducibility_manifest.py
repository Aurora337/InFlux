#!/usr/bin/env python3
"""Generate deterministic release reproducibility manifest by replaying sync-ops audit chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from runtime_executable import python_cmd


REPRO_ARTIFACTS = [
    "testnet/launch/sync_ops_finalization_pipeline.json",
    "testnet/launch/sync_ops_release_gate.json",
    "testnet/launch/sync_ops_audit_log.json",
    "testnet/launch/sync_ops_audit_log_validation.json",
    "testnet/launch/sync_ops_audit_assurance_pipeline.json",
    "testnet/launch/sync_ops_audit_assurance_pipeline_validation.json",
    "testnet/launch/sync_ops_audit_assurance_validation_pipeline.json",
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


def _snapshot(paths: list[str]) -> list[dict]:
    items = []
    for rel in paths:
        path = Path(rel)
        if not path.exists():
            items.append(
                {
                    "path": rel,
                    "exists": False,
                    "sha256": "",
                    "size_bytes": 0,
                }
            )
            continue
        items.append(
            {
                "path": rel,
                "exists": True,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return items


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def generate_repro_manifest(
    inject_failure_suite: str,
    inject_failure_attempt: int,
    min_readiness_score: int,
    release_version: str,
    output_json: Path,
    output_md: Path,
) -> dict:
    base_cmd = python_cmd(
        "scripts/testnet/run_sync_ops_audit_assurance_validation_pipeline.py",
        "--min-readiness-score",
        str(min_readiness_score),
        "--release-version",
        release_version,
    )
    if inject_failure_suite:
        base_cmd.extend(["--inject-failure-suite", inject_failure_suite])
    if inject_failure_attempt > 0:
        base_cmd.extend(["--inject-failure-attempt", str(inject_failure_attempt)])

    run_one = _run_step("replay_run_1", base_cmd)
    snapshot_one = _snapshot(REPRO_ARTIFACTS) if run_one["success"] else []

    run_two = _run_step("replay_run_2", base_cmd)
    snapshot_two = _snapshot(REPRO_ARTIFACTS) if run_two["success"] else []

    checks: list[dict] = []
    checks.append(_make_check("replay_run_1_success", run_one["success"], f"exit_code={run_one['exit_code']}"))
    checks.append(_make_check("replay_run_2_success", run_two["success"], f"exit_code={run_two['exit_code']}"))
    checks.append(
        _make_check(
            "snapshot_sizes_match",
            len(snapshot_one) == len(REPRO_ARTIFACTS) and len(snapshot_two) == len(REPRO_ARTIFACTS),
            f"run1={len(snapshot_one)} run2={len(snapshot_two)} expected={len(REPRO_ARTIFACTS)}",
        )
    )

    mismatch_paths: list[str] = []
    if snapshot_one and snapshot_two:
        for idx, item_one in enumerate(snapshot_one):
            item_two = snapshot_two[idx]
            path = item_one["path"]
            exists_match = item_one["exists"] == item_two["exists"]
            sha_match = item_one["sha256"] == item_two["sha256"]
            size_match = item_one["size_bytes"] == item_two["size_bytes"]
            all_match = exists_match and sha_match and size_match
            checks.append(
                _make_check(
                    f"artifact_reproducible::{path}",
                    all_match,
                    (
                        f"exists={item_one['exists']}/{item_two['exists']} "
                        f"size={item_one['size_bytes']}/{item_two['size_bytes']} "
                        f"sha={item_one['sha256']}/{item_two['sha256']}"
                    ),
                )
            )
            if not all_match:
                mismatch_paths.append(path)

    terminal_report = _load_json(Path("testnet/launch/sync_ops_audit_assurance_validation_pipeline.json"))
    terminal_summary = terminal_report.get("summary", {}) if terminal_report else {}

    checks.append(
        _make_check(
            "terminal_pipeline_success",
            bool(terminal_report.get("pipeline_success", False)),
            f"pipeline_success={terminal_report.get('pipeline_success', False)}",
        )
    )
    checks.append(
        _make_check(
            "terminal_pipeline_validation_valid",
            bool(terminal_summary.get("pipeline_validation_valid", False)),
            f"pipeline_validation_valid={terminal_summary.get('pipeline_validation_valid', False)}",
        )
    )
    checks.append(
        _make_check(
            "terminal_audit_valid",
            bool(terminal_summary.get("audit_valid", False)),
            f"audit_valid={terminal_summary.get('audit_valid', False)}",
        )
    )

    failed = [item for item in checks if not item["passed"]]
    reproducible = len(failed) == 0

    manifest = {
        "suite": "v1.0.6-sync-ops-reproducibility-manifest",
        "reproducible": reproducible,
        "release_version": release_version,
        "injected_failure": {
            "suite": inject_failure_suite or "none",
            "attempt": inject_failure_attempt,
        },
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": [item["check"] for item in failed],
        "mismatch_paths": mismatch_paths,
        "terminal_summary": {
            "release_decision": terminal_summary.get("release_decision", "unknown"),
            "certificate_status": terminal_summary.get("certificate_status", "unknown"),
            "audit_valid": bool(terminal_summary.get("audit_valid", False)),
            "audit_checks_passed": int(terminal_summary.get("audit_checks_passed", 0)),
            "audit_checks_total": int(terminal_summary.get("audit_checks_total", 0)),
            "pipeline_validation_valid": bool(terminal_summary.get("pipeline_validation_valid", False)),
            "pipeline_validation_checks_passed": int(terminal_summary.get("pipeline_validation_checks_passed", 0)),
            "pipeline_validation_checks_total": int(terminal_summary.get("pipeline_validation_checks_total", 0)),
        },
        "replay_runs": [run_one, run_two],
        "run_1_artifacts": snapshot_one,
        "run_2_artifacts": snapshot_two,
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v1.0.6 Sync Ops Reproducibility Manifest",
        "",
        f"- Reproducible: {manifest['reproducible']}",
        f"- Release Version: {manifest['release_version']}",
        f"- Checks: {manifest['checks_passed']}/{manifest['checks_total']}",
        f"- Mismatch Paths: {len(manifest['mismatch_paths'])}",
        "",
        "## Terminal Summary",
        "",
        f"- release_decision={manifest['terminal_summary']['release_decision']}",
        f"- certificate_status={manifest['terminal_summary']['certificate_status']}",
        f"- audit_valid={manifest['terminal_summary']['audit_valid']}",
        (
            f"- audit_checks={manifest['terminal_summary']['audit_checks_passed']}/"
            f"{manifest['terminal_summary']['audit_checks_total']}"
        ),
        f"- pipeline_validation_valid={manifest['terminal_summary']['pipeline_validation_valid']}",
        (
            f"- pipeline_validation_checks={manifest['terminal_summary']['pipeline_validation_checks_passed']}/"
            f"{manifest['terminal_summary']['pipeline_validation_checks_total']}"
        ),
        "",
        "## Replay Runs",
        "",
    ]

    for run in manifest["replay_runs"]:
        lines.append(f"- step={run['step']} success={run['success']} exit_code={run['exit_code']}")
        for out in run["stdout_tail"]:
            lines.append(f"  - stdout: {out}")

    lines.extend(["", "## Checks", ""])
    for check in manifest["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync-ops reproducibility manifest")
    parser.add_argument("--inject-failure-suite", default="", help="Suite id to force failure in supervisor attempt")
    parser.add_argument("--inject-failure-attempt", type=int, default=0, help="Attempt index for injected failure")
    parser.add_argument("--min-readiness-score", type=int, default=85, help="Minimum readiness score threshold")
    parser.add_argument("--release-version", default="1.0.5", help="Release version string for audit log")
    parser.add_argument("--output-json", default="testnet/launch/sync_ops_reproducibility_manifest.json")
    parser.add_argument("--output-md", default="testnet/launch/sync_ops_reproducibility_manifest.md")
    args = parser.parse_args()

    manifest = generate_repro_manifest(
        inject_failure_suite=args.inject_failure_suite,
        inject_failure_attempt=args.inject_failure_attempt,
        min_readiness_score=args.min_readiness_score,
        release_version=args.release_version,
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Reproducible: {manifest['reproducible']}")
    print(f"Checks Passed: {manifest['checks_passed']}/{manifest['checks_total']}")
    print(f"Mismatch Paths: {len(manifest['mismatch_paths'])}")
    print(f"Release Decision: {manifest['terminal_summary']['release_decision']}")
    print(f"Audit Valid: {manifest['terminal_summary']['audit_valid']}")
    print(f"Pipeline Validation Valid: {manifest['terminal_summary']['pipeline_validation_valid']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()