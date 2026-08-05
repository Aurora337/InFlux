from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class UpgradeRecord:
    """
    Deterministic contract upgrade record.
    """

    contract_id: str
    previous_version: str
    new_version: str
    migration_id: str
    height: int

    def to_dict(self) -> dict[str, Any]:
        """
        Export deterministic upgrade data.
        """

        return {
            "contract_id": self.contract_id,
            "previous_version": self.previous_version,
            "new_version": self.new_version,
            "migration_id": self.migration_id,
            "height": self.height,
        }

    def is_upgrade(self) -> bool:
        """
        Determine whether this represents
        an actual version transition.
        """

        return (
            self.previous_version
            != self.new_version
        )