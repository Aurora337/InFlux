#!/usr/bin/env python3
"""Validate deterministic sync operations promotion packet integrity and consistency."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def _expected_decision(gate: dict, min_score: int) -> str:
    gate_passed = bool(gate.get("gate_passed", False))
    readiness_score = int(gate.get("readiness_score", 0))
    recommendation = gate.get("promotion_recommendation", "hold")
    escalated = bool(gate.get("escalated", False))
    failed_checks = gate.get("failed_checks", [])

    has_blockers = (not gate_passed) or bool(failed_checks) or escalated or (readiness_score < min_score)

    if has_blockers:
        if escalated or recommendation == "block":
            return "block"
        return "hold"

    if recommendation in {"promote", "promote_with_monitoring"}:
        return recommendation

    return "hold"


def validate_promotion_packet(
    runbook_path: Path,
    handoff_path: Path,
    gate_path: Path,
    packet_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    runbook = _load_json(runbook_path)
    handoff = _load_json(handoff_path)
    gate = _load_json(gate_path)
    packet = _load_json(packet_path)

    checks: list[dict] = []

    checks.append(_make_check("runbook_present", bool(runbook), f"path={runbook_path}"))
    checks.append(_make_check("handoff_present", bool(handoff), f"path={handoff_path}"))
    checks.append(_make_check("gate_present", bool(gate), f"path={gate_path}"))
    checks.append(_make_check("packet_present", bool(packet), f"path={packet_path}"))

    if runbook and handoff and gate and packet:
        checks.append(
            _make_check(
                "packet_gate_passed_consistent",
                bool(packet.get("gate_passed", False)) == bool(gate.get("gate_passed", False)),
                f"packet={packet.get('gate_passed')} gate={gate.get('gate_passed')}",
            )
        )

        checks.append(
            _make_check(
                "packet_score_consistent",
                int(packet.get("readiness_score", 0)) == int(gate.get("readiness_score", 0)),
                f"packet={packet.get('readiness_score')} gate={gate.get('readiness_score')}",
            )
        )

        checks.append(
            _make_check(
                "packet_recommendation_consistent",
                packet.get("promotion_recommendation", "hold") == gate.get("promotion_recommendation", "hold"),
                f"packet={packet.get('promotion_recommendation')} gate={gate.get('promotion_recommendation')}",
            )
        )

        checks.append(
            _make_check(
                "packet_operational_state_consistent",
                packet.get("operational_state", "unknown") == gate.get("operational_state", runbook.get("operational_state", "unknown")),
                f"packet={packet.get('operational_state')} gate={gate.get('operational_state')}",
            )
        )

        expected_decision = _expected_decision(gate=gate, min_score=int(packet.get("min_readiness_score", 0)))
        checks.append(
            _make_check(
                "packet_decision_consistent",
                packet.get("promotion_decision", "hold") == expected_decision,
                f"packet={packet.get('promotion_decision')} expected={expected_decision}",
            )
        )

        manifest = packet.get("artifact_manifest", [])
        expected_paths = [str(runbook_path), str(handoff_path), str(gate_path)]
        checks.append(
            _make_check(
                "artifact_manifest_size",
                len(manifest) == 3,
                f"manifest_items={len(manifest)} expected=3",
            )
        )

        manifest_paths = [item.get("path", "") for item in manifest]
        checks.append(
            _make_check(
                "artifact_manifest_paths",
                manifest_paths == expected_paths,
                f"manifest_paths={manifest_paths}",
            )
        )

        for item in manifest:
            path = Path(item.get("path", ""))
            exists = bool(item.get("exists", False))
            size_bytes = int(item.get("size_bytes", 0))
            recorded_hash = item.get("sha256", "")

            if not path.exists():
                checks.append(_make_check(f"artifact_exists::{path}", not exists, f"path missing on disk: {path}"))
                continue

            actual_size = path.stat().st_size
            actual_hash = _sha256(path)

            checks.append(
                _make_check(
                    f"artifact_exists::{path}",
                    exists,
                    f"packet_exists={exists} actual_exists=True",
                )
            )
            checks.append(
                _make_check(
                    f"artifact_size::{path}",
                    size_bytes == actual_size,
                    f"packet_size={size_bytes} actual_size={actual_size}",
                )
            )
            checks.append(
                _make_check(
                    f"artifact_hash::{path}",
                    recorded_hash == actual_hash,
                    f"packet_sha256={recorded_hash} actual_sha256={actual_hash}",
                )
            )

    failed_checks = [item for item in checks if not item["passed"]]
    packet_valid = len(failed_checks) == 0

    report = {
        "suite": "v0.9.1-sync-ops-promotion-packet-validator",
        "packet_valid": packet_valid,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed_checks),
        "checks_failed": len(failed_checks),
        "failed_checks": [item["check"] for item in failed_checks],
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.1 Sync Ops Promotion Packet Validation",
        "",
        f"- Packet Valid: {report['packet_valid']}",
        f"- Checks Total: {report['checks_total']}",
        f"- Checks Passed: {report['checks_passed']}",
        f"- Checks Failed: {report['checks_failed']}",
        "",
        "## Checks",
        "",
    ]

    for check in report["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    if report["failed_checks"]:
        lines.extend(["", "## Failed Checks", ""])
        for check_name in report["failed_checks"]:
            lines.append(f"- {check_name}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic sync ops promotion packet")
    parser.add_argument("--runbook", default="testnet/launch/sync_ops_runbook.json", help="Runbook JSON path")
    parser.add_argument("--handoff", default="testnet/launch/sync_ops_handoff_note.json", help="Handoff JSON path")
    parser.add_argument("--gate", default="testnet/launch/sync_ops_stability_gate.json", help="Stability gate JSON path")
    parser.add_argument("--packet", default="testnet/launch/sync_ops_promotion_packet.json", help="Promotion packet JSON path")
    parser.add_argument("--output-json", default="testnet/launch/sync_ops_promotion_packet_validation.json", help="Validation JSON output path")
    parser.add_argument("--output-md", default="testnet/launch/sync_ops_promotion_packet_validation.md", help="Validation markdown output path")
    args = parser.parse_args()

    report = validate_promotion_packet(
        runbook_path=Path(args.runbook),
        handoff_path=Path(args.handoff),
        gate_path=Path(args.gate),
        packet_path=Path(args.packet),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Packet Valid: {report['packet_valid']}")
    print(f"Checks Passed: {report['checks_passed']}/{report['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
