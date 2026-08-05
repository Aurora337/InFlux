from __future__ import annotations

from dataclasses import dataclass, field

from .migration import ContractMigration
from .validator import MigrationValidator


@dataclass(slots=True)
class MigrationExecutor:
    """
    Deterministic migration executor.
    """

    validator: MigrationValidator = field(
        default_factory=MigrationValidator
    )

    executed: list[ContractMigration] = field(
        default_factory=list
    )

    def execute(
        self,
        migration: ContractMigration,
    ) -> bool:
        """
        Execute a validated migration.
        """

        if not self.validator.validate(migration):
            return False

        self.executed.append(migration)
        return True

    def latest(self) -> ContractMigration:
        """
        Return the most recently executed migration.
        """

        if not self.executed:
            raise ValueError(
                "No migrations executed."
            )

        return self.executed[-1]

    def count(self) -> int:
        """
        Return the number of executed migrations.
        """

        return len(self.executed)