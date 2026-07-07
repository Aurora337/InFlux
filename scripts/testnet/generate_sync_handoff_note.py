#!/usr/bin/env python3
"""Generate deterministic post-incident sync handoff notes from runbook output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _priority_rank(severity: str) -> int:
    if severity == "critical":
        return 0
    if severity == "high":
        return 1
    if severity == "medium":
        return 2
    return 3


def generate_handoff(runbook_path: Path, output_json: Path, output_md: Path) -> dict:
    runbook = _load_json(runbook_path)

    incident_actions = runbook.get("incident_actions", [])
    incident_timeline = runbook.get("incident_timeline", [])

    sorted_actions = sorted(
        incident_actions,
        key=lambda item: (_priority_rank(item.get("severity", "low")), item.get("failure_reason", "none")),
    )

    top_actions: list[dict] = []
    for item in sorted_actions[:3]:
        top_actions.append(
            {
                "failure_reason": item.get("failure_reason", "none"),
                "severity": item.get("severity", "low"),
                "scenario": item.get("scenario", "unknown"),
                "first_action": (item.get("actions", ["No action"])[0]),
            }
        )

    recent_events = incident_timeline[-5:] if len(incident_timeline) > 5 else incident_timeline

    handoff = {
        "suite": "v0.8.9-sync-operations-handoff",
        "operational_state": runbook.get("operational_state", "unknown"),
        "escalated": runbook.get("escalated", False),
        "recovered_after_retry": runbook.get("recovered_after_retry", False),
        "policy_winner": runbook.get("policy_winner", "unknown"),
        "top_actions": top_actions,
        "recent_timeline_events": recent_events,
        "shift_handoff_summary": {
            "retry_summary": runbook.get("retry_summary", {}),
            "latency_summary": runbook.get("latency_summary", {}),
            "orchestration_summary": runbook.get("orchestration_summary", {}),
        },
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(handoff, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.9 Sync Operations Handoff Note",
        "",
        f"- Operational State: {handoff['operational_state']}",
        f"- Escalated: {handoff['escalated']}",
        f"- Recovered After Retry: {handoff['recovered_after_retry']}",
        f"- Policy Winner: {handoff['policy_winner']}",
        "",
        "## Immediate Actions",
        "",
    ]

    for action in top_actions:
        lines.append(
            f"- severity={action['severity']} reason={action['failure_reason']} scenario={action['scenario']} action={action['first_action']}"
        )

    lines.extend(
        [
            "",
            "## Recent Timeline",
            "",
        ]
    )

    for event in recent_events:
        lines.append(
            f"- T+{event.get('t_plus_seconds', 0)}s event={event.get('event', 'unknown')} severity={event.get('severity', 'low')} details={event.get('details', '')}"
        )

    lines.extend(
        [
            "",
            "## Shift Summary",
            "",
            f"- Retry: {handoff['shift_handoff_summary']['retry_summary']}",
            f"- Latency: {handoff['shift_handoff_summary']['latency_summary']}",
            f"- Orchestration: {handoff['shift_handoff_summary']['orchestration_summary']}",
        ]
    )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return handoff


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync operations handoff note")
    parser.add_argument(
        "--runbook",
        default="testnet/launch/sync_ops_runbook.json",
        help="Runbook JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_handoff_note.json",
        help="Handoff JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_handoff_note.md",
        help="Handoff markdown output path",
    )
    args = parser.parse_args()

    handoff = generate_handoff(
        runbook_path=Path(args.runbook),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Operational State: {handoff['operational_state']}")
    print(f"Escalated: {handoff['escalated']}")
    print(f"Recovered After Retry: {handoff['recovered_after_retry']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
