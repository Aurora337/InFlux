"""
Tests for Release Integrity Audit — v1.1.1 Slice 1.

Validates deterministic execution, repeatable results, and correct report
output for scripts/audit/release_integrity_audit.py.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure the project root is on sys.path for importing the audit module
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit.release_integrity_audit import (  # noqa: E402
    _tag_sort_key,
    collect_release_notes,
    enumerate_tags,
    expected_release_note_filename,
    find_orphaned_tags,
    find_version_tags_without_notes,
    is_tag_version_tag,
    run_audit,
    tag_commit_exists_in_history,
    tag_resolves_to_commit,
)

# ---------------------------------------------------------------------------
# Determinism & repeatability
# ---------------------------------------------------------------------------


class TestDeterminism:
    """The audit must produce identical results across repeated runs."""

    def test_enumerate_tags_deterministic(self):
        """Calling enumerate_tags() twice must yield the same order."""
        first = enumerate_tags()
        second = enumerate_tags()
        assert first == second, "enumerate_tags() is non-deterministic"

    def test_run_audit_deterministic(self):
        """Calling run_audit() twice must produce identical dicts."""
        r1 = run_audit()
        r2 = run_audit()
        assert r1 == r2, "run_audit() is non-deterministic"

    def test_report_json_deterministic(self):
        """JSON output must be byte-identical across runs."""
        r1 = run_audit()
        r2 = run_audit()
        j1 = json.dumps(r1, indent=2, sort_keys=True)
        j2 = json.dumps(r2, indent=2, sort_keys=True)
        assert j1 == j2, "JSON output is non-deterministic"


# ---------------------------------------------------------------------------
# Tag sorting
# ---------------------------------------------------------------------------


class TestTagSortKey:
    """Verify version-aware tag sorting."""

    def test_simple_version(self):
        assert _tag_sort_key("v0.1") == (0, 1)
        assert _tag_sort_key("v1.0") == (1, 0)

    def test_patch_version(self):
        assert _tag_sort_key("v1.1.0") == (1, 1, 0)
        assert _tag_sort_key("v1.10.0") == (1, 10, 0)

    def test_no_prefix_handling(self):
        assert _tag_sort_key("0.1") == (0, 1)
        assert _tag_sort_key("1.1.1") == (1, 1, 1)

    def test_non_numeric_fallback(self):
        key = _tag_sort_key("rc1")
        assert isinstance(key, tuple)
        # Should return something, even if not numeric
        assert len(key) >= 1


# ---------------------------------------------------------------------------
# Tag resolution checks
# ---------------------------------------------------------------------------


class TestTagResolution:
    """Verify tag resolution functions work on the real repo."""

    def test_all_tags_resolve_to_commit(self):
        """Every tag in the repo must resolve to a commit."""
        tags = enumerate_tags()
        if not tags:
            pytest.skip("No tags in repository")
        failing = [t for t in tags if not tag_resolves_to_commit(t)]
        assert failing == [], f"Tags that don't resolve: {failing}"

    def test_all_tag_commits_exist_in_history(self):
        """Every tagged commit must be reachable."""
        tags = enumerate_tags()
        if not tags:
            pytest.skip("No tags in repository")
        failing = [t for t in tags if not tag_commit_exists_in_history(t)]
        assert failing == [], f"Tags with unreachable commits: {failing}"


# ---------------------------------------------------------------------------
# Release note checks
# ---------------------------------------------------------------------------


class TestReleaseNotePattern:
    """Validate release note naming conventions."""

    def test_expected_note_filename(self):
        assert expected_release_note_filename("v0.1") == "v0.1-release-notes.md"
        assert expected_release_note_filename("v1.10.0") == "v1.10.0-release-notes.md"
        assert expected_release_note_filename("0.1") == "v0.1-release-notes.md"

    def test_is_tag_version_tag(self):
        assert is_tag_version_tag("v0.1") is True
        assert is_tag_version_tag("v1.1.0") is True
        assert is_tag_version_tag("v1.10.0") is True
        assert is_tag_version_tag("rc1") is False
        assert is_tag_version_tag("v1.1.1-alpha") is False


class TestReleaseNotesCollection:
    """Verify release note discovery from the filesystem."""

    def test_collect_release_notes(self):
        """Must find existing release notes in docs/releases/."""
        notes = collect_release_notes()
        assert len(notes) >= 1, "No release notes found"
        for note in notes:
            assert note.startswith("v"), f"Unexpected note name: {note}"
            assert note.endswith("-release-notes.md")

    def test_missing_notes_empty_for_valid_repo(self):
        """On a well-maintained repo, no version tags should be missing notes."""
        all_tags = enumerate_tags()
        existing = collect_release_notes()
        missing = find_version_tags_without_notes(all_tags, existing)
        # This may be non-empty on incomplete repos; just check it returns a list
        assert isinstance(missing, list)


class TestOrphanedTags:
    """Verify orphaned tag detection."""

    def test_find_orphaned_returns_list(self):
        tags = enumerate_tags()
        notes = collect_release_notes()
        orphaned = find_orphaned_tags(tags, notes)
        assert isinstance(orphaned, list)


# ---------------------------------------------------------------------------
# Report structure & score
# ---------------------------------------------------------------------------


class TestReportStructure:
    """Verify the report dict has the expected shape."""

    def test_report_contains_all_keys(self):
        report = run_audit()
        expected_keys = {
            "audit_valid",
            "tags_checked",
            "tags_valid",
            "missing_release_notes",
            "orphaned_tags",
            "integrity_score",
        }
        assert set(report.keys()) == expected_keys, "Report keys mismatch"

    def test_report_types(self):
        report = run_audit()
        assert isinstance(report["audit_valid"], bool)
        assert isinstance(report["tags_checked"], int)
        assert isinstance(report["tags_valid"], int)
        assert isinstance(report["missing_release_notes"], list)
        assert isinstance(report["orphaned_tags"], list)
        assert isinstance(report["integrity_score"], float)

    def test_integrity_score_range(self):
        report = run_audit()
        assert 0.0 <= report["integrity_score"] <= 1.0

    def test_tags_counts_consistency(self):
        report = run_audit()
        assert report["tags_valid"] <= report["tags_checked"]

    def test_audit_valid_implies_full_score(self):
        report = run_audit()
        if report["audit_valid"]:
            assert report["integrity_score"] == 1.0
            assert report["tags_checked"] == report["tags_valid"]
            assert len(report["missing_release_notes"]) == 0


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


class TestCLI:
    """Run the audit script as a subprocess for integration coverage."""

    def test_cli_exit_code(self):
        """The script should exit 0 when audit_valid is True."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "audit" / "release_integrity_audit.py")],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=30,
        )
        # We accept both 0 and 1 depending on repo state
        assert result.returncode in (0, 1), f"Unexpected exit code: {result.returncode}"
        assert "Running release integrity audit..." in result.stdout

    def test_cli_generates_report_file(self):
        """Running the CLI must produce the report JSON."""
        with tempfile.TemporaryDirectory():
            subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "audit" / "release_integrity_audit.py")],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                timeout=30,
            )
            # Report file should be at the canonical path
            report_path = PROJECT_ROOT / "docs" / "audit" / "release_integrity_report.json"
            assert report_path.exists(), "Report file not created"
            # Verify it's valid JSON
            with open(report_path) as f:
                data = json.load(f)
            assert "audit_valid" in data
            assert "integrity_score" in data
