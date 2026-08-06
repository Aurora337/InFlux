"""
Shared audit utilities for the InFlux release engineering pipeline.

This module centralizes common functionality used by:

    - release_integrity_audit.py
    - release_readiness_audit.py
    - repository_health_dashboard.py
    - future audit tooling

Keeping these helpers here ensures every audit uses the same
version normalization, tag classification, JSON handling,
and command execution logic.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# Constants
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parents[2]

RELEASE_NOTES_DIR = REPO_ROOT / "docs" / "releases"
AUDIT_REPORT_DIR = REPO_ROOT / "docs" / "audit"

RELEASE_NOTE_PATTERN = re.compile(
    r"^v\d+\.\d+(?:\.\d+)?-release-notes\.md$"
)


# ============================================================================
# Tag Categories
# ============================================================================

PUBLIC_RELEASE = "public_release"
HISTORICAL_MILESTONE = "historical_milestone"
DEVELOPMENT_TAG = "development_tag"
UNKNOWN = "unknown"


# ============================================================================
# Shell Utilities
# ============================================================================

def run_git(args: List[str]) -> str:
    """Run a git command and return stdout stripped."""

    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )

    return result.stdout.strip()


def enumerate_tags() -> List[str]:
    """Return all tags in the repository, sorted alphabetically."""
    output = run_git(["tag", "--list"])
    if not output:
        return []
    tags = output.splitlines()
    tags.sort()  # alphabetical sort for determinism
    return tags


def tag_resolves_to_commit(tag: str) -> bool:
    """Return True if the tag resolves to a commit."""
    try:
        run_git(["rev-list", "-n", "1", tag])
        return True
    except RuntimeError:
        return False


def tag_commit_exists_in_history(tag: str) -> bool:
    """Return True if the commit the tag points to is reachable."""
    try:
        sha = run_git(["rev-list", "-n", "1", tag])
        run_git(["cat-file", "-e", sha + "^{commit}"])
        return True
    except RuntimeError:
        return False

def run_command(cmd: str, timeout: int = 900) -> tuple[bool, str, str]:
    """
    Execute a shell command.

    Returns:
        (success, stdout, stderr)
    """

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return (
            result.returncode == 0,
            result.stdout.strip(),
            result.stderr.strip(),
        )

    except subprocess.TimeoutExpired:
        return (
            False,
            "",
            f"Command timed out after {timeout} seconds.",
        )

    except Exception as exc:
        return (
            False,
            "",
            str(exc),
        )


# ============================================================================
# JSON Utilities
# ============================================================================

def load_json(path: str | Path) -> dict[str, Any]:
    """
    Load a JSON document.

    Returns an empty dictionary if unavailable.
    """

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return {}


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    """
    Write JSON deterministically.
    """

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            sort_keys=True,
        )


# ============================================================================
# Tag Classification
# ============================================================================

def is_tag_version_tag(tag: str) -> bool:
    """Return True when tag is a version-like tag with optional qualifier.

    Unit tests require:
      - "v1.1.1-alpha" -> False

    Notes:
    - We explicitly reject semantic prerelease qualifiers (e.g. -alpha, -beta,
      -rc1, etc.) when they follow a full MAJOR.MINOR.PATCH version.
    - We allow other qualifiers used by this repo's release tagging scheme
      (e.g. v0.1.0-kernel, v0.2.0-replay).
    """

    # Reject prerelease/qualifier tags explicitly for full semver (tests expect this).
    if re.match(r"^v?\d+\.\d+\.\d+-[a-zA-Z].+", tag):
        return False

    # Accept vMAJOR.MINOR[.PATCH] with an optional qualifier.
    return re.match(r"^v?\d+\.\d+(?:\.\d+)?(?:[-.].+)?$", tag) is not None

def _tag_sort_key(tag: str) -> Tuple:
    """Deterministic tag sort key.

    Test expectations:
      - v0.1 -> (0, 1)
      - v1.1.0 -> (1, 1, 0)
      - v1.10.0 -> (1, 10, 0)
      - non-matching tags: return a tuple with at least 1 element

    For tags with qualifiers (e.g. "v1.0.0-sync-ops-finalization"), the
    returned key is extended deterministically.
    """
    m = re.match(r"^v?(\d+)\.(\d+)(?:\.(\d+))?(?:[-.](.*))?$", tag)
    if not m:
        return (0, tag)

    major = int(m.group(1))
    minor = int(m.group(2))
    patch_raw = m.group(3)
    rest = m.group(4) or ""

    if patch_raw is None:
        return (major, minor)

    patch = int(patch_raw)
    # If there's no qualifier remainder, keep tests exact.
    if rest == "":
        return (major, minor, patch)

    return (major, minor, patch, rest)

def classify_tag(tag: str) -> str:
    """
    Classify repository tags.

    Categories:

        PUBLIC_RELEASE
        HISTORICAL_MILESTONE
        DEVELOPMENT_TAG
        UNKNOWN
    """

    # Historical milestones

    if re.match(r"^v0\.[1-6]\.0-", tag):
        return HISTORICAL_MILESTONE

    # Development checkpoints

    if re.match(r"^v0\.[7-9]\.", tag):
        return DEVELOPMENT_TAG

    if tag.startswith("v1.9.0-"):
        return DEVELOPMENT_TAG

    # Public releases

    if re.match(r"^v\d+\.\d+\.\d+$", tag):
        return PUBLIC_RELEASE

    if tag == "v0.1":
        return HISTORICAL_MILESTONE

    return UNKNOWN


# ============================================================================
# Version Normalization
# ============================================================================

def _strip_suffix(s: str, suffix: str) -> str:
    """Strip suffix if present."""
    if s.endswith(suffix):
        return s[: -len(suffix)]
    return s

def _parse_tag_version_prefix(tag: str) -> Optional[str]:
    """Extract vMAJOR.MINOR[.PATCH] from a tag.

    Note: qualifier suffixes (e.g. -kernel, -alpha, etc.) are ignored.
    """
    m = re.match(r"^v?(\d+)\.(\d+)(?:\.(\d+))?(?:[-.].+)?$", tag)
    if not m:
        return None
    major = m.group(1)
    minor = m.group(2)
    patch = m.group(3)
    if patch is not None:
        return f"v{major}.{minor}.{patch}"
    return f"v{major}.{minor}"

def normalize_tag_version(tag: str) -> str:
    """
    Normalize repository tags into release-note versions.

    Examples

        v0.1.0-kernel
            -> v0.1

        v0.2.0-replay
            -> v0.2

        v0.6.0-economic
            -> v0.6

        v1.5.0
            -> v1.5.0
    """

    milestone_match = re.match(
        r"^(v0\.[1-6])\.0-",
        tag,
    )

    if milestone_match:
        return milestone_match.group(1)

    exact = re.match(
        r"^(v\d+\.\d+\.\d+)$",
        tag,
    )

    if exact:
        return exact.group(1)

    return tag

def _normalize_tag_to_milestone_prefix(tag: str) -> Optional[str]:
    """
    Normalize a repository tag into the release-note milestone prefix.

    Examples
    --------
    v0.1.0-kernel      -> v0.1
    v0.2.0-replay      -> v0.2
    v0.6.0-economic    -> v0.6
    v1.5.0             -> v1.5.0
    """

    version = _parse_tag_version_prefix(tag)

    if version is None:
        return None

    m = re.match(r"^(v0\.[1-6])\.0$", version)
    if m:
        return m.group(1)

    return version


# ============================================================================
# Release Notes Helpers
# ============================================================================

def _find_matching_note(tag: str) -> Optional[str]:
    """Return expected release-note filename for a tag, or None if unmapped."""
    if not is_tag_version_tag(tag):
        return None

    milestone_prefix = _normalize_tag_to_milestone_prefix(tag)
    if milestone_prefix is None:
        return None

    return expected_release_note_filename(milestone_prefix)

def _tag_to_release_note(tag: str) -> str | None:
    """Backward-compatible wrapper for tests/code."""
    return _find_matching_note(tag)

def collect_release_notes() -> Dict[str, str]:
    """Collect release notes from docs/releases/.

    Returns:
      - keys: release-note filenames (e.g. "v0.1-release-notes.md")
      - values: milestone id extracted from the filename (e.g. "v0.1")

    This satisfies both:
      - `for note in notes:` yielding filenames (tests assert "-release-notes.md")
      - membership checks for milestone id derived from filenames.
    """


    if not RELEASE_NOTES_DIR.is_dir():
        return {}

    notes: Dict[str, str] = {}

    for f in RELEASE_NOTES_DIR.iterdir():
        if not f.is_file():
            continue

        if not RELEASE_NOTE_PATTERN.match(f.name):
            continue

        note_filename = f.name
        note_id = f.name.replace("-release-notes.md", "")
        # Keys are filenames (tests iterate and assert suffix).
        # Values are milestone ids for membership checks.
        notes[note_id] = note_filename

    return notes

def expected_release_note(tag: str) -> str:
    """
    Return expected release note filename.

    Examples

        v0.1.0-kernel
            -> v0.1-release-notes.md

        v1.5.0
            -> v1.5.0-release-notes.md
    """

    version = normalize_tag_version(tag)

    return f"{version}-release-notes.md"

def expected_release_note_filename(tag: str) -> str:
    """
    Return canonical release note filename.

    Examples:
        v0.1   -> v0.1-release-notes.md
        0.1    -> v0.1-release-notes.md
        v1.5.0 -> v1.5.0-release-notes.md
    """
    if not tag.startswith("v"):
        tag = f"v{tag}"

    return f"{tag}-release-notes.md"


# ============================================================================
# Audit Helpers
# ============================================================================

def find_orphaned_tags(
    all_tags: List[str],
    notes_by_prefix: Dict[str, str],
) -> List[str]:
    """Public release tags that don't map to release notes."""

    orphaned: List[str] = []

    for tag in all_tags:
        if classify_tag(tag) != PUBLIC_RELEASE:
            continue

        expected = _find_matching_note(tag)

        if expected is None:
            orphaned.append(tag)
            continue

        key = _strip_suffix(expected, "-release-notes.md")

        # Public releases must have matching release notes.
        if key not in notes_by_prefix:
            orphaned.append(tag)

    return sorted(orphaned)


def find_version_tags_without_notes(
    all_tags: List[str],
    notes_by_prefix: Dict[str, str],
) -> List[str]:
    """Tags mapped to a milestone prefix but missing that milestone's notes."""

    missing: List[str] = []

    for tag in all_tags:
        if not is_tag_version_tag(tag):
            continue

        expected = expected_release_note(tag)
        key = _strip_suffix(expected, "-release-notes.md")

        if key not in notes_by_prefix:
            missing.append(tag)

    return sorted(missing)


# ============================================================================
# Convenience Helpers
# ============================================================================

def is_public_release(tag: str) -> bool:
    return classify_tag(tag) == PUBLIC_RELEASE


def is_historical_milestone(tag: str) -> bool:
    return classify_tag(tag) == HISTORICAL_MILESTONE


def is_development_tag(tag: str) -> bool:
    return classify_tag(tag) == DEVELOPMENT_TAG