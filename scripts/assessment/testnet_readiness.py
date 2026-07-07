#!/usr/bin/env python3
"""Deterministic testnet readiness scoring for v1.3.2.

This script converts protocol assessment findings into a deterministic
readiness score and emits both JSON and markdown artifacts.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


STATUS_SCORES = {
    "implemented": 1.0,
    "partial": 0.65,
    "missing": 0.0,
}

OVERALL_THRESHOLD = 0.80
DOMAIN_FLOOR = 0.60


@dataclass(frozen=True)
class Criterion:
    name: str
    status: str
    evidence: str


BASELINE_PROFILE: dict[str, list[Criterion]] = {
    "consensus": [
        Criterion("implemented", "partial", "Simulation-grade consensus is present; production engine remains incomplete."),
        Criterion("deterministic", "implemented", "Deterministic simulation and audit artifacts exist."),
        Criterion("multi_node_capable", "partial", "Multi-node behavior exists in simulator/harness, not as persistent runtime nodes."),
    ],
    "validator_lifecycle": [
        Criterion("creation", "partial", "Validator roles and configs exist but lifecycle controls are incomplete."),
        Criterion("registration", "missing", "No production registration/admission path is wired as runtime behavior."),
        Criterion("startup", "partial", "Startup scaffolding exists without full operational orchestration."),
        Criterion("shutdown", "partial", "Shutdown behavior is represented in scripts, not complete runtime controls."),
        Criterion("recovery", "missing", "Recovery flows for rejoin and state catch-up are not complete."),
    ],
    "peer_discovery": [
        Criterion("static", "partial", "Static peer/config scaffolding exists for testnet artifacts."),
        Criterion("dynamic", "missing", "Dynamic peer discovery protocol is not implemented."),
        Criterion("missing", "missing", "Peer discovery stack remains a known gap from protocol assessment."),
    ],
    "state_replication": [
        Criterion("hash_agreement", "partial", "Hash verification exists in tests and verification scripts."),
        Criterion("snapshot_exchange", "missing", "Snapshot/state exchange service is not implemented end-to-end."),
        Criterion("recovery", "partial", "Recovery validation exists in scripts but not full runtime service behavior."),
    ],
    "replay_engine": [
        Criterion("deterministic_replay", "implemented", "Replay scenarios and deterministic replay checks are present."),
        Criterion("verification", "implemented", "Replay verification tooling is present and used."),
        Criterion("recovery", "partial", "Replay recovery integration still depends on prototype pathways."),
    ],
    "ledger": [
        Criterion("persistence", "partial", "Ledger primitives exist, but production durability semantics need hardening."),
        Criterion("verification", "implemented", "Ledger verification tooling exists and is regularly used."),
        Criterion("auditability", "partial", "Audit artifacts exist, but runtime ledger audit traceability is not fully integrated."),
    ],
    "economics": [
        Criterion("verification_engine", "implemented", "Economic verification engine is present."),
        Criterion("simulation_coverage", "implemented", "Economic scenario simulation coverage is broad and deterministic."),
        Criterion("audit_coverage", "implemented", "Economic audit reports are generated and validated."),
    ],
}


def _score_for_status(status: str) -> float:
    if status not in STATUS_SCORES:
        raise ValueError(f"Unknown criterion status: {status}")
    return STATUS_SCORES[status]


def score_domain(criteria: list[Criterion]) -> float:
    if not criteria:
        return 0.0
    total = sum(_score_for_status(item.status) for item in criteria)
    return round(total / len(criteria), 2)


def build_readiness_report() -> dict:
    domain_scores = {domain: score_domain(criteria) for domain, criteria in BASELINE_PROFILE.items()}
    readiness_score = round(sum(domain_scores.values()) / len(domain_scores), 2)

    blockers = [
        domain
        for domain, score in domain_scores.items()
        if score < DOMAIN_FLOOR
    ]
    testnet_ready = readiness_score >= OVERALL_THRESHOLD and not blockers

    report = {
        "testnet_ready": testnet_ready,
        "readiness_score": readiness_score,
        "consensus": domain_scores["consensus"],
        "validator_lifecycle": domain_scores["validator_lifecycle"],
        "peer_discovery": domain_scores["peer_discovery"],
        "state_replication": domain_scores["state_replication"],
        "replay_engine": domain_scores["replay_engine"],
        "ledger": domain_scores["ledger"],
        "economics": domain_scores["economics"],
        "thresholds": {
            "overall": OVERALL_THRESHOLD,
            "minimum_domain": DOMAIN_FLOOR,
        },
        "blocking_domains": blockers,
        "criteria": {
            domain: {
                item.name: item.status for item in criteria
            }
            for domain, criteria in BASELINE_PROFILE.items()
        },
        "artifact_sources": [
            "docs/architecture/protocol_gap_analysis.md",
            "docs/architecture/protocol_inventory.md",
            "docs/architecture/testnet_readiness_assessment.md",
        ],
        "status_scale": STATUS_SCORES,
    }
    return report


def _write_json(report: dict, output_json: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def _write_markdown(report: dict, output_md: Path) -> None:
    domain_rows = [
        ("consensus", "Implemented / Deterministic / Multi-node capable"),
        ("validator_lifecycle", "Creation / Registration / Startup / Shutdown / Recovery"),
        ("peer_discovery", "Static / Dynamic / Missing"),
        ("state_replication", "Hash agreement / Snapshot exchange / Recovery"),
        ("replay_engine", "Deterministic replay / Verification / Recovery"),
        ("ledger", "Persistence / Verification / Auditability"),
        ("economics", "Verification engine / Simulation coverage / Audit coverage"),
    ]

    lines = [
        "# InFlux Testnet Readiness Assessment (v1.3.2)",
        "",
        "## Objective",
        "",
        "Convert protocol assessment artifacts into a deterministic testnet readiness score.",
        "",
        "## Deterministic Output",
        "",
        f"- testnet_ready: {str(report['testnet_ready']).lower()}",
        f"- readiness_score: {report['readiness_score']}",
        f"- threshold_overall: {report['thresholds']['overall']}",
        f"- threshold_minimum_domain: {report['thresholds']['minimum_domain']}",
        "",
        "## Domain Scores",
        "",
        "| Domain | Criteria | Score |",
        "|---|---|---:|",
    ]

    for domain, criteria_text in domain_rows:
        lines.append(f"| {domain} | {criteria_text} | {report[domain]:.2f} |")

    lines.extend(
        [
            "",
            "## Blocking Domains",
            "",
        ]
    )

    if report["blocking_domains"]:
        for item in report["blocking_domains"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Scoring Model",
            "",
            "- implemented = 1.00",
            "- partial = 0.65",
            "- missing = 0.00",
            "",
            "Each domain score is the arithmetic mean of its criterion scores. Overall readiness score is the arithmetic mean of the seven domain scores.",
            "",
            "## Sources",
            "",
        ]
    )

    for source in report["artifact_sources"]:
        lines.append(f"- {source}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic testnet readiness score")
    parser.add_argument(
        "--output-json",
        default="docs/architecture/testnet_readiness_score.json",
        help="Output JSON report path",
    )
    parser.add_argument(
        "--output-md",
        default="docs/architecture/testnet_readiness_assessment.md",
        help="Output markdown report path",
    )
    args = parser.parse_args()

    report = build_readiness_report()
    _write_json(report, Path(args.output_json))
    _write_markdown(report, Path(args.output_md))

    print(f"testnet_ready: {str(report['testnet_ready']).lower()}")
    print(f"readiness_score: {report['readiness_score']}")
    print(f"blocking_domains: {', '.join(report['blocking_domains']) if report['blocking_domains'] else 'none'}")
    print(f"report: {args.output_json}")
    print(f"report: {args.output_md}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()