"""
Contract version tracking and migration support.

Provides deterministic version management,
migration validation, and upgrade safety checks
for deployed smart contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .contract import Contract


@dataclass(frozen=True, slots=True)
class ContractVersion:
    """
    Deterministic contract version record.
    """

    contract_id: str
    version: str
    code_hash: str
    previous_code_hash: str | None = None
    migration_data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VersionRegistry:
    """
    Deterministic registry of contract versions.

    Tracks the full version history for each contract,
    enabling safe migration rollbacks and audit.
    """

    _versions: dict[str, list[ContractVersion]] = field(
        default_factory=dict,
    )
    _max_history: int = 10

    def record(
        self,
        contract_id: str,
        version: str,
        code_hash: str,
        previous_code_hash: str | None = None,
        migration_data: dict[str, Any] | None = None,
    ) -> ContractVersion:
        """
        Record a new contract version.
        """

        if contract_id not in self._versions:
            self._versions[contract_id] = []

        history = self._versions[contract_id]

        if len(history) >= self._max_history:
            history.pop(0)

        record = ContractVersion(
            contract_id=contract_id,
            version=version,
            code_hash=code_hash,
            previous_code_hash=previous_code_hash,
            migration_data=migration_data or {},
        )

        history.append(record)

        return record

    def get_current(
        self,
        contract_id: str,
    ) -> ContractVersion | None:
        """
        Get the current (latest) version of a contract.
        """

        history = self._versions.get(contract_id)

        if not history:
            return None

        return history[-1]

    def get_history(
        self,
        contract_id: str,
    ) -> list[ContractVersion]:
        """
        Get the full version history for a contract.
        """

        return list(self._versions.get(contract_id, []))

    def has_version(
        self,
        contract_id: str,
        version: str,
    ) -> bool:
        """
        Check if a specific version exists.
        """

        history = self._versions.get(contract_id)

        if not history:
            return False

        return any(
            record.version == version
            for record in history
        )

    def version_count(
        self,
        contract_id: str | None = None,
    ) -> int:
        """
        Return the number of recorded versions.
        """

        if contract_id is not None:
            return len(self._versions.get(contract_id, []))

        return sum(
            len(history)
            for history in self._versions.values()
        )

    def can_migrate(
        self,
        contract: Contract,
        target_version: str,
        current_code_hash: str,
    ) -> bool:
        """
        Check if a contract can be migrated to a target version.
        """

        current = self.get_current(contract.contract_id)

        if current is None:
            return True

        if current.code_hash != current_code_hash:
            return False

        if current.version == target_version:
            return False

        return True

    def reset(
        self,
        contract_id: str | None = None,
    ) -> None:
        """
        Reset version history.
        """

        if contract_id is not None:
            self._versions.pop(contract_id, None)
        else:
            self._versions.clear()


@dataclass(slots=True)
class UpgradeValidator:
    """
    Validates contract upgrades for safety and compatibility.

    Ensures that contract upgrades follow deterministic
    rules and do not break existing state.
    """

    def validate_upgrade(
        self,
        current: Contract,
        upgraded: Contract,
        current_storage_snapshot: dict[str, str] | None = None,
    ) -> tuple[bool, str]:
        """
        Validate a contract upgrade.

        Returns (is_valid, reason) tuple.
        """

        if current.contract_id != upgraded.contract_id:
            return (
                False,
                "Contract ID cannot change during upgrade.",
            )

        if current.owner != upgraded.owner:
            return (
                False,
                "Contract owner cannot change during upgrade.",
            )

        if current.version == upgraded.version:
            return (
                False,
                "Version must change during upgrade.",
            )

        if not upgraded.code_hash:
            return (
                False,
                "Upgraded contract must have a code hash.",
            )

        return (
            True,
            "Upgrade validation passed.",
        )

    def validate_migration(
        self,
        migration_fn_name: str,
        migration_data: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        """
        Validate a migration function call.

        Returns (is_valid, reason) tuple.
        """

        if not migration_fn_name:
            return (
                False,
                "Migration function name cannot be empty.",
            )

        if migration_data and not isinstance(migration_data, dict):
            return (
                False,
                "Migration data must be a dictionary.",
            )

        return (
            True,
            "Migration validation passed.",
        )
