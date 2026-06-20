#!/usr/bin/env python3
"""Generate deterministic sync operations runbook from resilience reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _severity_for_failure_reason(reason: str, escalated: bool) -> str:
    if escalated:
        return "critical"
    if reason == "retry_exhausted":
        return "high"
    if reason in {"suite_validation_failed", "injected_failure"}:
        return "medium"
    if reason == "none":
        return "low"
    return "medium"


def _actions_for_failure_reason(reason: str, escalated: bool) -> list[str]:
    if escalated:
        return [
            "Escalate to on-call synchronization lead immediately.",
            "Freeze non-essential sync jobs and collect all suite reports.",
            "Run targeted rerun with increased retry budget and capture new telemetry.",
        ]
    if reason == "retry_exhausted":
        return [
            "Increase retry budget for affected validator profile.",
            "Reduce replay chunk size to lower timeout pressure.",
            "Re-run retry exhaustion and orchestration supervisor suites.",
        ]
    if reason == "suite_validation_failed":
        return [
            "Inspect failing suite report details and failure reason fields.",
            "Re-run only the failed suite with deterministic parameters.",
            "If repeatable, open incident ticket with attached report artifacts.",
        ]
    if reason == "injected_failure":
        return [
            "No production action required; this indicates deterministic test injection.",
            "Verify supervisor recovered on next attempt.",
            "Record test evidence in release notes.",
        ]
    return [
        "No immediate action required.",
        "Maintain current sync policy and continue monitoring.",
    ]


def _collect_failure_reasons(retry_suite: dict, supervisor_suite: dict) -> list[dict]:
    reasons: dict[str, dict] = {}

    for result in retry_suite.get("results", []):
        reason = result.get("failure_reason", "none")
        reasons[reason] = {
            "reason": reason,
            "source": "retry_exhaustion_suite",
            "observed_success": result.get("observed_success", True),
            "scenario": result.get("id", "unknown"),
        }

    for attempt in supervisor_suite.get("attempts", []):
        for suite_result in attempt.get("suite_results", []):
            reason = suite_result.get("failure_reason", "none")
            reasons[reason] = {
                "reason": reason,
                "source": "orchestration_supervisor",
                "observed_success": suite_result.get("suite_passed", True),
                "scenario": f"attempt_{attempt.get('attempt', 0)}::{suite_result.get('suite_id', 'unknown')}",
            }

    return sorted(reasons.values(), key=lambda item: item["reason"])


def generate_runbook(
    retry_suite_path: Path,
    latency_suite_path: Path,
    policy_suite_path: Path,
    orchestration_path: Path,
    supervisor_path: Path,
    output_json: Path,
    output_md: Path,
) -> dict:
    retry_suite = _load_json(retry_suite_path)
    latency_suite = _load_json(latency_suite_path)
    policy_suite = _load_json(policy_suite_path)
    orchestration_suite = _load_json(orchestration_path)
    supervisor_suite = _load_json(supervisor_path)

    escalated = bool(supervisor_suite.get("escalated", False))
    recovered_after_retry = bool(supervisor_suite.get("recovered_after_retry", False))
    supervisor_success = bool(supervisor_suite.get("supervisor_success", False))
    policy_winner = (policy_suite.get("winner") or orchestration_suite.get("policy_winner") or {}).get("policy_id", "unknown")

    reason_entries = _collect_failure_reasons(retry_suite, supervisor_suite)

    incident_actions: list[dict] = []
    for entry in reason_entries:
        reason = entry["reason"]
        severity = _severity_for_failure_reason(reason, escalated)
        actions = _actions_for_failure_reason(reason, escalated)
        incident_actions.append(
            {
                "failure_reason": reason,
                "severity": severity,
                "source": entry["source"],
                "scenario": entry["scenario"],
                "actions": actions,
            }
        )

    operational_state = "stable"
    if escalated:
        operational_state = "critical"
    elif recovered_after_retry:
        operational_state = "degraded_recovered"

    report = {
        "suite": "v0.8.8-sync-operations-runbook",
        "operational_state": operational_state,
        "escalated": escalated,
        "recovered_after_retry": recovered_after_retry,
        "policy_winner": policy_winner,
        "retry_summary": {
            "scenarios": retry_suite.get("scenarios", 0),
            "passed": retry_suite.get("passed", 0),
            "expected_failures": retry_suite.get("expected_failures", 0),
            "observed_failures": retry_suite.get("observed_failures", 0),
        },
        "latency_summary": {
            "scenarios": latency_suite.get("scenarios", 0),
            "passed": latency_suite.get("passed", 0),
            "all_passed": latency_suite.get("all_passed", False),
        },
        "orchestration_summary": {
            "orchestration_success": bool(orchestration_suite.get("orchestration_success", supervisor_success)),
            "attempts_executed": supervisor_suite.get("attempts_executed", 0),
            "supervisor_success": supervisor_success,
        },
        "incident_actions": incident_actions,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.8.8 Sync Operations Runbook",
        "",
        f"- Operational State: {report['operational_state']}",
        f"- Escalated: {report['escalated']}",
        f"- Recovered After Retry: {report['recovered_after_retry']}",
        f"- Policy Winner: {report['policy_winner']}",
        "",
        "## Summary",
        "",
        f"- Retry: scenarios={report['retry_summary']['scenarios']} passed={report['retry_summary']['passed']} expected_failures={report['retry_summary']['expected_failures']} observed_failures={report['retry_summary']['observed_failures']}",
        f"- Latency: scenarios={report['latency_summary']['scenarios']} passed={report['latency_summary']['passed']} all_passed={report['latency_summary']['all_passed']}",
        f"- Orchestration: success={report['orchestration_summary']['orchestration_success']} supervisor_success={report['orchestration_summary']['supervisor_success']} attempts_executed={report['orchestration_summary']['attempts_executed']}",
        "",
        "## Incident Actions",
        "",
    ]

    for item in report["incident_actions"]:
        lines.append(
            f"- reason={item['failure_reason']} severity={item['severity']} source={item['source']} scenario={item['scenario']}"
        )
        for action in item["actions"]:
            lines.append(f"  - {action}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic sync operations runbook")
    parser.add_argument("--retry-suite", default="testnet/launch/retry_exhaustion_suite.json", help="Retry suite report path")
    parser.add_argument("--latency-suite", default="testnet/launch/backoff_latency_suite.json", help="Latency suite report path")
    parser.add_argument("--policy-suite", default="testnet/launch/policy_comparison_suite.json", help="Policy suite report path")
    parser.add_argument("--orchestration-suite", default="testnet/launch/sync_orchestration_report.json", help="Orchestration report path")
    parser.add_argument("--supervisor-suite", default="testnet/launch/sync_orchestration_supervisor_report.json", help="Supervisor report path")
    parser.add_argument("--output-json", default="testnet/launch/sync_ops_runbook.json", help="Runbook JSON output path")
    parser.add_argument("--output-md", default="testnet/launch/sync_ops_runbook.md", help="Runbook markdown output path")
    args = parser.parse_args()

    report = generate_runbook(
        retry_suite_path=Path(args.retry_suite),
        latency_suite_path=Path(args.latency_suite),
        policy_suite_path=Path(args.policy_suite),
        orchestration_path=Path(args.orchestration_suite),
        supervisor_path=Path(args.supervisor_suite),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Operational State: {report['operational_state']}")
    print(f"Escalated: {report['escalated']}")
    print(f"Recovered After Retry: {report['recovered_after_retry']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
