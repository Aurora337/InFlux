from __future__ import annotations

from dataclasses import dataclass, field

from .migration import ContractMigration


@dataclass(slots=True)
class MigrationRegistry:
    """
    Deterministic migration registry.
    """

    migrations: dict[str, ContractMigration] = field(
        default_factory=dict
    )

    def register(
        self,
        migration: ContractMigration,
    ) -> bool:
        """
        Register a migration.
        """

        if migration.migration_id in self.migrations:
            return False

        self.migrations[migration.migration_id] = migration
        return True

    def get(
        self,
        migration_id: str,
    ) -> ContractMigration:
        """
        Retrieve a migration.
        """

        return self.migrations[migration_id]

    def count(self) -> int:
        """
        Number of registered migrations.
        """

        return len(self.migrations)