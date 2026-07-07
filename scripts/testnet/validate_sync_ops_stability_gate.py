#!/usr/bin/env python3
"""Validate deterministic sync operations stability gates from runbook and handoff artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED_OPERATIONAL_STATES = {"stable", "degraded_recovered", "critical"}


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _rank(severity: str) -> int:
    if severity == "critical":
        return 0
    if severity == "high":
        return 1
    if severity == "medium":
        return 2
    return 3


def _make_check(name: str, passed: bool, details: str) -> dict:
    return {
        "check": name,
        "passed": passed,
        "details": details,
    }


def _build_state_guidance(operational_state: str, escalated: bool, gate_passed: bool) -> list[str]:
    if not gate_passed:
        return [
            "Block release promotion until all failed checks are resolved.",
            "Regenerate runbook and handoff artifacts after fixes and rerun the stability gate.",
        ]

    if escalated or operational_state == "critical":
        return [
            "Keep promotion blocked while escalation remains active.",
            "Run targeted recovery suites and obtain a non-critical operational state before release.",
        ]

    if operational_state == "degraded_recovered":
        return [
            "Promotion is allowed with monitoring due to recovered degraded state.",
            "Run one additional supervisor verification and archive artifacts with release notes.",
        ]

    return [
        "Promotion is allowed for stable state.",
        "Proceed with standard release checklist and retain stability artifacts for traceability.",
    ]


def _calculate_readiness_score(checks_total: int, checks_failed: int, operational_state: str, escalated: bool) -> int:
    score = 100
    score -= checks_failed * 15

    if escalated:
        score -= 30
    elif operational_state == "critical":
        score -= 25
    elif operational_state == "degraded_recovered":
        score -= 10

    if checks_total == 0:
        score = 0

    if score < 0:
        return 0
    if score > 100:
        return 100
    return score


def _promotion_recommendation(gate_passed: bool, operational_state: str, escalated: bool) -> str:
    if not gate_passed:
        return "hold"
    if escalated or operational_state == "critical":
        return "block"
    if operational_state == "degraded_recovered":
        return "promote_with_monitoring"
    return "promote"


def _verify_top_actions(runbook_actions: list[dict], handoff_actions: list[dict]) -> tuple[bool, str]:
    if not handoff_actions:
        return False, "handoff top_actions is empty"

    runbook_map: dict[tuple[str, str], dict] = {}
    for item in runbook_actions:
        key = (item.get("failure_reason", "none"), item.get("scenario", "unknown"))
        runbook_map[key] = item

    last_rank = -1
    for index, action in enumerate(handoff_actions):
        reason = action.get("failure_reason", "none")
        scenario = action.get("scenario", "unknown")
        severity = action.get("severity", "low")
        first_action = action.get("first_action", "")

        rank = _rank(severity)
        if index == 0:
            last_rank = rank
        else:
            if rank < last_rank:
                return False, "handoff top_actions are not sorted by severity priority"
            last_rank = rank

        key = (reason, scenario)
        if key not in runbook_map:
            return False, f"handoff top_action reason={reason} scenario={scenario} not found in runbook incident_actions"

        runbook_first_action = (runbook_map[key].get("actions", [""])[0])
        if runbook_first_action != first_action:
            return (
                False,
                f"handoff first_action mismatch for reason={reason} scenario={scenario}: expected '{runbook_first_action}' got '{first_action}'",
            )

    return True, f"validated {len(handoff_actions)} prioritized actions against runbook"


def _verify_recent_timeline(runbook_timeline: list[dict], handoff_recent: list[dict]) -> tuple[bool, str]:
    if not handoff_recent:
        return False, "handoff recent_timeline_events is empty"

    if len(handoff_recent) > 5:
        return False, "handoff recent_timeline_events exceeds max expected size of 5"

    expected_suffix = runbook_timeline[-len(handoff_recent) :] if runbook_timeline else []
    if expected_suffix != handoff_recent:
        return False, "handoff recent_timeline_events is not the expected suffix of runbook incident_timeline"

    return True, f"validated {len(handoff_recent)} recent timeline events as deterministic suffix"


def validate_stability_gate(runbook_path: Path, handoff_path: Path, output_json: Path, output_md: Path) -> dict:
    runbook = _load_json(runbook_path)
    handoff = _load_json(handoff_path)
    operational_state = runbook.get("operational_state", "unknown") if runbook else "unknown"
    escalated = bool(runbook.get("escalated", False)) if runbook else False

    checks: list[dict] = []

    checks.append(
        _make_check(
            "runbook_present",
            bool(runbook),
            "runbook JSON loaded" if runbook else f"missing or empty runbook at {runbook_path}",
        )
    )
    checks.append(
        _make_check(
            "handoff_present",
            bool(handoff),
            "handoff JSON loaded" if handoff else f"missing or empty handoff at {handoff_path}",
        )
    )

    if runbook and handoff:
        runbook_state = runbook.get("operational_state", "unknown")
        handoff_state = handoff.get("operational_state", "unknown")
        checks.append(
            _make_check(
                "operational_state_allowed",
                runbook_state in ALLOWED_OPERATIONAL_STATES,
                f"runbook operational_state={runbook_state}",
            )
        )
        checks.append(
            _make_check(
                "operational_state_consistent",
                runbook_state == handoff_state,
                f"runbook={runbook_state} handoff={handoff_state}",
            )
        )

        for field_name in ["escalated", "recovered_after_retry", "policy_winner"]:
            checks.append(
                _make_check(
                    f"{field_name}_consistent",
                    runbook.get(field_name) == handoff.get(field_name),
                    f"runbook={runbook.get(field_name)} handoff={handoff.get(field_name)}",
                )
            )

        actions_ok, actions_details = _verify_top_actions(
            runbook_actions=runbook.get("incident_actions", []),
            handoff_actions=handoff.get("top_actions", []),
        )
        checks.append(_make_check("top_actions_consistent", actions_ok, actions_details))

        timeline_ok, timeline_details = _verify_recent_timeline(
            runbook_timeline=runbook.get("incident_timeline", []),
            handoff_recent=handoff.get("recent_timeline_events", []),
        )
        checks.append(_make_check("recent_timeline_consistent", timeline_ok, timeline_details))

    failed_checks = [item for item in checks if not item["passed"]]
    gate_passed = len(failed_checks) == 0
    readiness_score = _calculate_readiness_score(
        checks_total=len(checks),
        checks_failed=len(failed_checks),
        operational_state=operational_state,
        escalated=escalated,
    )
    promotion_recommendation = _promotion_recommendation(
        gate_passed=gate_passed,
        operational_state=operational_state,
        escalated=escalated,
    )
    guidance = _build_state_guidance(
        operational_state=operational_state,
        escalated=escalated,
        gate_passed=gate_passed,
    )

    report = {
        "suite": "v0.9.0-sync-ops-stability-gate",
        "gate_passed": gate_passed,
        "readiness_score": readiness_score,
        "promotion_recommendation": promotion_recommendation,
        "operational_state": operational_state,
        "escalated": escalated,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed_checks),
        "checks_failed": len(failed_checks),
        "failed_checks": [item["check"] for item in failed_checks],
        "guidance": guidance,
        "checks": checks,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# v0.9.0 Sync Ops Stability Gate",
        "",
        f"- Gate Passed: {report['gate_passed']}",
        f"- Readiness Score: {report['readiness_score']}/100",
        f"- Promotion Recommendation: {report['promotion_recommendation']}",
        f"- Operational State: {report['operational_state']}",
        f"- Escalated: {report['escalated']}",
        f"- Checks Total: {report['checks_total']}",
        f"- Checks Passed: {report['checks_passed']}",
        f"- Checks Failed: {report['checks_failed']}",
        "",
        "## Guidance",
        "",
    ]

    for line in report["guidance"]:
        lines.append(f"- {line}")

    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        lines.append(f"- {check['check']}: passed={check['passed']} details={check['details']}")

    if report["failed_checks"]:
        lines.extend(
            [
                "",
                "## Failed Checks",
                "",
            ]
        )
        for item in report["failed_checks"]:
            lines.append(f"- {item}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic sync operations stability gates")
    parser.add_argument(
        "--runbook",
        default="testnet/launch/sync_ops_runbook.json",
        help="Runbook JSON path",
    )
    parser.add_argument(
        "--handoff",
        default="testnet/launch/sync_ops_handoff_note.json",
        help="Handoff JSON path",
    )
    parser.add_argument(
        "--output-json",
        default="testnet/launch/sync_ops_stability_gate.json",
        help="Stability gate JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="testnet/launch/sync_ops_stability_gate.md",
        help="Stability gate markdown output path",
    )
    args = parser.parse_args()

    report = validate_stability_gate(
        runbook_path=Path(args.runbook),
        handoff_path=Path(args.handoff),
        output_json=Path(args.output_json),
        output_md=Path(args.output_md),
    )

    print(f"Gate Passed: {report['gate_passed']}")
    print(f"Readiness Score: {report['readiness_score']}")
    print(f"Promotion Recommendation: {report['promotion_recommendation']}")
    print(f"Checks Passed: {report['checks_passed']}/{report['checks_total']}")
    print(f"Report: {args.output_json}")
    print(f"Report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
