#!/usr/bin/env python3
"""Generate deterministic sync operations promotion packet from runbook, handoff, and stability gate artifacts."""

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


def _artifact_record(path: Path) -> dict:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "size_bytes": 0,
            "sha256": "",
        }

    return {
        "path": str(path),
        "exists": True,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _promotion_decision(gate: dict, min_score: int) -> tuple[str, list[str]]:
    blockers: list[str] = []

    gate_passed = bool(gate.get("gate_passed", False))
    readiness_score = int(gate.get("readiness_score", 0))
    recommendation = gate.get("promotion_recommendation", "hold")
    escalated = bool(gate.get("escalated", False))
    failed_checks = gate.get("failed_checks", [])

    if not gate_passed:
        blockers.append("stability_gate_failed")
    if failed_checks:
        blockers.append("failed_checks_present")
    if escalated:
        blockers.append("escalation_active")
    if readiness_score < min_score:
        blockers.append(f"readiness_below_threshold:{readiness_score}<{min_score}")

    if blockers:
        if escalated or recommendation == "block":
            return "block", blockers
        return "hold", blockers

    if recommendation in {"promote", "promote_with_monitoring"}:
        return recommendation, blockers

    return "hold", blockers


def generate_promotion_packet(
    runbook_path: Path,
    handoff_path: Path,
    gate_path: Path,
    output_json: Path,
    output_md: Path,
    min_readiness_score: int,
) -> dict:
    runbook = _load_json(runbook_path)
    handoff = _load_json(handoff_path)
    gate = _load_json(gate_path)

    decision, blockers = _promotion_decision(gate=gate, min_score=min_readiness_score)

    artifact_manifest = [
        _artifact_record(runbook_path),
        _artifact_record(handoff_path),
        _artifact_record(gate_path),
    ]

    next_actions = list(gate.get("guidance", []))
    for item in handoff.get("top_actions", [])[:2]:
        first_action = item.get("first_action", "")
        if first_action:
            next_actions.append(first_action)

    packet = {
        "suite": "v0.9.0-sync-ops-promotion-packet",
        "promotion_decision": decision,
        "min_readiness_score": min_readiness_score,
        "readiness_score": int(gate.get("readiness_score", 0)),
        "promotion_recommendation": gate.get("promotion_recommendation", "hold"),
        "operational_state": gate.get("operational_state", runbook.get("operational_state", "unknown")),
        "escalated": bool(gate.get("escalated", runbook.get("escalated", False))),
        "gate_passed": bool(gate.get("gate_passed", False)),
        "checks_passed": gate.get("checks_passed", 0),
        "checks_total": gate.get("checks_total", 0),
        "blockers": blockers,
        "artifact_manifest": artifact_manifest,
        "policy_winner": handoff.get("policy_winner", runbook.get("policy_winner", "unknown")),
        "next_actions": next_actions,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.0 Sync Ops Promotion Packet",
        "",
        f"- Promotion Decision: {packet['promotion_decision']}",
        f"- Promotion Recommendation: {packet['promotion_recommendation']}",
        f"- Readiness Score: {packet['readiness_score']}/{packet['min_readiness_score']} (threshold)",
        f"- Gate Passed: {packet['gate_passed']}",
        f"- Checks: {packet['checks_passed']}/{packet['checks_total']}",
        f"- Operational State: {packet['operational_state']}",
        f"- Escalated: {packet['escalated']}",
        f"- Policy Winner: {packet['policy_winner']}",
        "",
        "## Blockers",
        "",
    ]

    if packet["blockers"]:
        for blocker in packet["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Artifact Manifest",
        "",
    ])

    for artifact in packet["artifact_manifest"]:
        lines.append(
            f"- path={artifact['path']} exists={artifact['exists']} size_bytes={artifact['size_bytes']} sha256={artifact['sha256']}"
        )

    lines.extend([
        "",
        "## Next Actions",
        "",
    ])

    for action in packet["next_actions"]:
        lines.append(f"- {action}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync ops promotion packet")
    parser.add_argument("--runbook", default="testnet/launch/sync_ops_runbook.json", help="Runbook JSON path")
    parser.add_argument("--handoff", default="testnet/launch/sync_ops_handoff_note.json", help="Handoff JSON path")
    parser.add_argument("--gate", default="testnet/launch/sync_ops_stability_gate.json", help="Stability gate JSON path")
    parser.add_argument("--output-json", default="testnet/launch/sync_ops_promotion_packet.json", help="Promotion packet JSON output path")
    parser.add_argument("--output-md", default="testnet/launch/sync_ops_promotion_packet.md", help="Promotion packet markdown output path")
    parser.add_argument("--min-readiness-score", type=int, default=85, help="Minimum readiness score required for release promotion")
    args = parser.parse_args()

    packet = generate_promotion_packet(
        runbook_path=Path(args.runbook),
        handoff_path=Path(args.handoff),
        gate_path=Path(args.gate),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
        min_readiness_score=args.min_readiness_score,
    )

    print(f"Promotion Decision: {packet['promotion_decision']}")
    print(f"Readiness Score: {packet['readiness_score']}")
    print(f"Recommendation: {packet['promotion_recommendation']}")
    print(f"Blockers: {len(packet['blockers'])}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
