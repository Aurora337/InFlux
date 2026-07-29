"""
Tests for contract versioning module.
"""

from __future__ import annotations

from influx.contracts.versioning import VersionRegistry, UpgradeValidator
from influx.contracts.contract import Contract


def test_version_registry_record() -> None:
    """Test recording a version."""

    registry = VersionRegistry()

    record = registry.record(
        contract_id="test",
        version="1.0.0",
        code_hash="0xabc",
    )

    assert record.contract_id == "test"
    assert record.version == "1.0.0"
    assert record.code_hash == "0xabc"
    assert record.previous_code_hash is None


def test_version_registry_get_current() -> None:
    """Test getting current version."""

    registry = VersionRegistry()

    registry.record("test", "1.0.0", "0xabc")
    registry.record("test", "1.1.0", "0xdef")

    current = registry.get_current("test")
    assert current is not None
    assert current.version == "1.1.0"


def test_version_registry_get_history() -> None:
    """Test getting version history."""

    registry = VersionRegistry()

    registry.record("test", "1.0.0", "0xabc")
    registry.record("test", "1.1.0", "0xdef")

    history = registry.get_history("test")
    assert len(history) == 2
    assert history[0].version == "1.0.0"
    assert history[1].version == "1.1.0"


def test_version_registry_has_version() -> None:
    """Test checking if version exists."""

    registry = VersionRegistry()

    registry.record("test", "1.0.0", "0xabc")

    assert registry.has_version("test", "1.0.0")
    assert not registry.has_version("test", "2.0.0")


def test_version_registry_can_migrate() -> None:
    """Test migration validation."""

    registry = VersionRegistry()

    contract = Contract(
        contract_id="test",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc",
    )

    registry.record("test", "1.0.0", "0xabc")

    # Can migrate to new version with matching code hash
    assert registry.can_migrate(contract, "1.1.0", "0xabc")

    # Cannot migrate with wrong code hash
    assert not registry.can_migrate(contract, "1.1.0", "0xwrong")


def test_version_registry_max_history() -> None:
    """Test max history enforcement."""

    registry = VersionRegistry(_max_history=3)

    for i in range(5):
        registry.record("test", f"1.{i}.0", f"0x{i}")

    history = registry.get_history("test")
    assert len(history) == 3
    assert history[0].version == "1.2.0"
    assert history[-1].version == "1.4.0"


def test_upgrade_validator_passes() -> None:
    """Test upgrade validation passes."""

    validator = UpgradeValidator()

    current = Contract(
        contract_id="test",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc",
    )

    upgraded = Contract(
        contract_id="test",
        owner="alice",
        version="1.1.0",
        code_hash="0xdef",
    )

    is_valid, reason = validator.validate_upgrade(current, upgraded)
    assert is_valid
    assert "passed" in reason


def test_upgrade_validator_fails_id_change() -> None:
    """Test upgrade fails if contract ID changes."""

    validator = UpgradeValidator()

    current = Contract("a", "alice", "1.0.0", "0xabc")
    upgraded = Contract("b", "alice", "1.1.0", "0xdef")

    is_valid, reason = validator.validate_upgrade(current, upgraded)
    assert not is_valid
    assert "ID" in reason


def test_upgrade_validator_fails_owner_change() -> None:
    """Test upgrade fails if owner changes."""

    validator = UpgradeValidator()

    current = Contract("test", "alice", "1.0.0", "0xabc")
    upgraded = Contract("test", "bob", "1.1.0", "0xdef")

    is_valid, reason = validator.validate_upgrade(current, upgraded)
    assert not is_valid
    assert "owner" in reason


def test_upgrade_validator_fails_same_version() -> None:
    """Test upgrade fails if version unchanged."""

    validator = UpgradeValidator()

    current = Contract("test", "alice", "1.0.0", "0xabc")
    upgraded = Contract("test", "alice", "1.0.0", "0xdef")

    is_valid, reason = validator.validate_upgrade(current, upgraded)
    assert not is_valid
    assert "Version" in reason


def test_validate_migration() -> None:
    """Test migration validation."""

    validator = UpgradeValidator()

    is_valid, reason = validator.validate_migration("migrate_v2", {"key": "value"})
    assert is_valid

    is_valid, reason = validator.validate_migration("")
    assert not is_valid
