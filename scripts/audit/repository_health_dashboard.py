#!/usr/bin/env python3
"""Repository Health Dashboard — v1.1.1 Slice 2.

Generates docs/audit/repository_health.json with deterministic metrics:
  - branch_count
  - tag_count
  - release_count (docs/releases/*-release-notes.md)
  - audit_count (docs/audits/*.md)
  - test_count (tests/**/*.py)
  - missing_docs[]
  - missing_audits[]
  - health_valid + health_score

Deterministic JSON serialization:
  - UTF-8, indent=2, sort_keys=True, ensure_ascii=False, plus trailing newline

Exit code:
  - 0 if health_valid is true
  - 1 otherwise
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_RELEASES_DIR = REPO_ROOT / "docs" / "releases"
DOCS_AUDITS_DIR = REPO_ROOT / "docs" / "audits"
AUDIT_REPORT_DIR = REPO_ROOT / "docs" / "audit"
REPOSITORY_HEALTH_PATH = AUDIT_REPORT_DIR / "repository_health.json"


def _run_git(args: List[str]) -> str:
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _count_git_branches() -> int:
    # Local branches only; deterministic because output ordering is stable.
    out = _run_git(["branch", "--list"])
    if not out:
        return 0
    # Lines look like: "* main" or "  feature/foo"; strip whitespace and optional '*'.
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    normalized = [ln[1:].strip() if ln.startswith("*") else ln for ln in lines]
    return len([ln for ln in normalized if ln])


def _count_git_tags() -> int:
    out = _run_git(["tag", "--list"])
    if not out:
        return 0
    tags = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return len(tags)


def _count_release_notes() -> int:
    if not DOCS_RELEASES_DIR.is_dir():
        return 0
    count = 0
    for f in DOCS_RELEASES_DIR.iterdir():
        if not f.is_file():
            continue
        if f.name.endswith("-release-notes.md"):
            count += 1
    return count


def _count_audits() -> int:
    if not DOCS_AUDITS_DIR.is_dir():
        return 0
    count = 0
    for f in DOCS_AUDITS_DIR.iterdir():
        if not f.is_file():
            continue
        if f.name.endswith(".md"):
            count += 1
    return count


def _count_tests_py() -> int:
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.is_dir():
        return 0
    # Deterministic because filesystem traversal isn't ordered; we only need a count.
    return sum(1 for p in tests_dir.rglob("*.py") if p.is_file())


def _sorted_missing(paths: List[Path]) -> List[str]:
    missing = [str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p) for p in paths if not p.exists()]
    missing.sort()
    return missing


def collect_repository_health() -> Dict:
    branch_count = _count_git_branches()
    tag_count = _count_git_tags()
    release_count = _count_release_notes()
    audit_count = _count_audits()
    test_count = _count_tests_py()

    # Missing docs/audits checks for Slice 2.
    required_docs = [
        REPO_ROOT / "docs" / "releases" / "index.md",
        AUDIT_REPORT_DIR / "release_integrity_report.json",
    ]
    required_audits = [
        AUDIT_REPORT_DIR / "release_integrity_report.json",
    ]

    missing_docs = _sorted_missing(required_docs)
    missing_audits = _sorted_missing(required_audits)

    health_valid = len(missing_docs) == 0 and len(missing_audits) == 0

    # Deterministic scoring: fully valid => 1.0, otherwise penalize based on missing lists.
    if health_valid:
        health_score = 1.0
    else:
        # Basic deterministic scheme: start at 1.0 then subtract fraction of missing items.
        denom = max(1, len(required_docs) + len(required_audits))
        missing_total = len(missing_docs) + len(missing_audits)
        health_score = round(max(0.0, 1.0 - (missing_total / denom)), 4)

    return {
        "health_valid": health_valid,
        "branch_count": int(branch_count),
        "tag_count": int(tag_count),
        "release_count": int(release_count),
        "audit_count": int(audit_count),
        "test_count": int(test_count),
        "missing_docs": missing_docs,
        "missing_audits": missing_audits,
        "health_score": float(health_score),
    }


def write_report(report: Dict) -> None:
    AUDIT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPOSITORY_HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    report = collect_repository_health()
    write_report(report)
    print(f"Repository health valid: {report['health_valid']}")
    print(f"Health score: {report['health_score']}")
    print(f"Report written to: {REPOSITORY_HEALTH_PATH}")
    return 0 if report["health_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())

