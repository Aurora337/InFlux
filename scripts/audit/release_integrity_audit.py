#!/usr/bin/env python3
"""
Release Integrity Audit — v1.1.1 Slice 1.

Verifies that every published tag corresponds to a valid release state:

1. Enumerate all repository tags.
2. Verify each tag resolves to a commit.
3. Verify tagged commits exist in repository history.
4. Verify release notes exist for each milestone.
5. Verify release note naming consistency.
6. Produce deterministic output.

Output: docs/audit/release_integrity_report.json
Exit code: 0 when audit_valid == true, 1 when audit_valid == false.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scripts.audit.common import (
    collect_release_notes,
    enumerate_tags,
    expected_release_note,
    find_orphaned_tags,
    find_version_tags_without_notes,
    run_git,
    tag_commit_exists_in_history,
    tag_resolves_to_commit,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_REPORT_DIR = REPO_ROOT / "docs" / "audit"
AUDIT_REPORT_PATH = AUDIT_REPORT_DIR / "release_integrity_report.json"

# Release notes naming pattern:
# - v<major>.<minor>-release-notes.md
# - v<major>.<minor>.<patch>-release-notes.md


# Release note mapping rules:
#   v0.1*  -> docs/releases/v0.1-release-notes.md
#   v0.2*  -> docs/releases/v0.2-release-notes.md
#   v0.3*  -> docs/releases/v0.3-release-notes.md
#   v0.4*  -> docs/releases/v0.4-release-notes.md
#   v0.5*  -> docs/releases/v0.5-release-notes.md
#   v0.6*  -> docs/releases/v0.6-release-notes.md
#   v1.0*  -> docs/releases/v1.0-release-notes.md
#   v1.1*  -> docs/releases/v1.1-release-notes.md


def run_audit() -> Dict:
    """Execute the full release integrity audit and return the report dict."""
    all_tags = enumerate_tags()
    available_notes = collect_release_notes()

    # -- Tag checks ----------------------------------------------------------
    invalid_tags: List[str] = []
    valid_tags: List[str] = []

    for tag in all_tags:
        resolves = tag_resolves_to_commit(tag)
        exists = tag_commit_exists_in_history(tag)
        if resolves and exists:
            valid_tags.append(tag)
        else:
            invalid_tags.append(tag)

    # -- Release note checks -------------------------------------------------
    missing_release_notes = find_version_tags_without_notes(
        all_tags,
        available_notes,
    )

    orphaned_tags = find_orphaned_tags(
        all_tags,
        available_notes,
    )


    # -- Score calculation ---------------------------------------------------
    tags_checked = len(all_tags)
    tags_valid = len(valid_tags)
    integrity_score = round(tags_valid / tags_checked, 4) if tags_checked > 0 else 0.0

    # -- Deterministic output ------------------------------------------------
    invalid_tags.sort()
    missing_release_notes.sort()
    orphaned_tags.sort()

    audit_valid = (
        integrity_score == 1.0
        and tags_checked == tags_valid
        and not missing_release_notes
        and not orphaned_tags
    )

    return {
        "audit_valid": audit_valid,
        "tags_checked": tags_checked,
        "tags_valid": tags_valid,
        "missing_release_notes": missing_release_notes,
        "orphaned_tags": orphaned_tags,
        "integrity_score": integrity_score,
    }



def write_report(report: Dict) -> None:
    """Write the audit report as UTF-8 JSON."""
    AUDIT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    """Entry point. Returns 0 when audit_valid, 1 otherwise."""
    print("Running release integrity audit...", flush=True)
    report = run_audit()

    print(f"  Tags checked:      {report['tags_checked']}")
    print(f"  Tags valid:        {report['tags_valid']}")
    print(f"  Integrity score:   {report['integrity_score']}")
    print(f"  Audit valid:       {report['audit_valid']}")
    if report["missing_release_notes"]:
        print(f"  Missing notes:     {', '.join(report['missing_release_notes'])}")
    if report["orphaned_tags"]:
        print(f"  Orphaned tags:     {', '.join(report['orphaned_tags'])}")


    write_report(report)
    print(f"\nReport written to {AUDIT_REPORT_PATH}")

    return 0 if report["audit_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
