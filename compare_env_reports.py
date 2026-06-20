#!/usr/bin/env python3
"""Compare environment reports for cross-platform determinism validation."""

import argparse
import glob
import json


def _load_report(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_reports(paths: list[str]) -> dict:
    reports = [_load_report(path) for path in paths]
    if not reports:
        return {
            "reports_checked": 0,
            "cross_platform_determinism": "FAIL",
            "reason": "No report files found",
            "reference_hash": None,
            "environments": [],
        }

    reference_hash = reports[0]["final_state_hash"]
    hash_matches = all(report["final_state_hash"] == reference_hash for report in reports)
    determinism_matches = all(report["replay_determinism_score"] == 1.0 for report in reports)
    integrity_matches = all(report["ledger_integrity"] == "PASS" for report in reports)

    status = "PASS" if (hash_matches and determinism_matches and integrity_matches) else "FAIL"

    return {
        "reports_checked": len(reports),
        "cross_platform_determinism": status,
        "reference_hash": reference_hash,
        "hash_match_all": hash_matches,
        "determinism_score_all_1": determinism_matches,
        "ledger_integrity_all_pass": integrity_matches,
        "environments": [
            {
                "environment": report["environment"],
                "final_state_hash": report["final_state_hash"],
                "replay_determinism_score": report["replay_determinism_score"],
                "scenario_determinism_score": report["scenario_determinism_score"],
                "consensus_agreement_rate": report["consensus_agreement_rate"],
                "ledger_integrity": report["ledger_integrity"],
            }
            for report in reports
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare environment determinism reports")
    parser.add_argument("--report", action="append", help="Report JSON file path (can repeat)")
    parser.add_argument("--glob", dest="glob_pattern", help="Glob pattern for report files")
    args = parser.parse_args()

    paths = args.report or []
    if args.glob_pattern:
        paths.extend(sorted(glob.glob(args.glob_pattern)))

    payload = compare_reports(paths)
    print(json.dumps(payload, indent=2))

    return 0 if payload["cross_platform_determinism"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
