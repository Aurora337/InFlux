from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ContractMigration:
    """
    Immutable deterministic contract migration.
    """

    migration_id: str
    contract_id: str
    from_version: str
    to_version: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        """
        Export deterministic migration representation.
        """
        return {
            "migration_id": self.migration_id,
            "contract_id": self.contract_id,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "description": self.description,
        }

    def is_upgrade(self) -> bool:
        """
        Return True if this migration changes versions.
        """
        return self.from_version != self.to_version