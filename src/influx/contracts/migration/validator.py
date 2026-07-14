from __future__ import annotations

from dataclasses import dataclass

from .migration import ContractMigration


@dataclass(slots=True)
class MigrationValidator:
    """
    Deterministic migration validator.
    """

    def validate(
        self,
        migration: ContractMigration,
    ) -> bool:

        if not migration.migration_id:
            return False

        if not migration.contract_id:
            return False

        if not migration.from_version:
            return False

        if not migration.to_version:
            return False

        if not migration.description:
            return False

        if not migration.is_upgrade():
            return False

        return True