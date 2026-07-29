"""
Tests for versioning vectors using the new VersionRegistry.
"""

from __future__ import annotations

from influx.contracts.versioning import VersionRegistry


def test_create_version():
    """Test creating a version record."""

    registry = VersionRegistry()

    registry.record("test", "1.0.0", "0xabc")

    assert registry.has_version("test", "1.0.0")


def test_restore_version():
    """Test version history tracking."""

    registry = VersionRegistry()

    registry.record("test", "1.0.0", "0xabc")
    registry.record("test", "1.1.0", "0xdef")

    current = registry.get_current("test")
    assert current is not None
    assert current.version == "1.1.0"


def test_versions_are_sorted():
    """Test versions are returned in order."""

    registry = VersionRegistry()

    registry.record("test", "1.0.0", "0xabc")
    registry.record("test", "1.1.0", "0xdef")
    registry.record("test", "2.0.0", "0xghi")

    history = registry.get_history("test")
    assert len(history) == 3
    assert history[0].version == "1.0.0"
    assert history[1].version == "1.1.0"
    assert history[2].version == "2.0.0"


def test_duplicate_version_recorded():
    """Test duplicate version is recorded (allows duplicates)."""

    registry = VersionRegistry()

    registry.record("test", "1.0.0", "0xabc")
    registry.record("test", "1.0.0", "0xabc")

    assert registry.version_count("test") == 2


def test_unknown_version_fails():
    """Test unknown version returns None."""

    registry = VersionRegistry()

    assert not registry.has_version("test", "99.0.0")


def test_versioning_is_deterministic():
    """Test versioning is deterministic across instances."""

    registry_a = VersionRegistry()
    registry_b = VersionRegistry()

    registry_a.record("test", "1.0.0", "0xabc")
    registry_b.record("test", "1.0.0", "0xabc")

    assert registry_a.get_history("test") == registry_b.get_history("test")
