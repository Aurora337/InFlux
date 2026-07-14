from __future__ import annotations

from dataclasses import dataclass, field

from .record import UpgradeRecord
from .validator import UpgradeValidator


@dataclass(slots=True)
class UpgradeController:
    """
    Deterministic contract upgrade controller.
    """

    validator: UpgradeValidator = field(
        default_factory=UpgradeValidator
    )

    records: list[UpgradeRecord] = field(
        default_factory=list
    )

    def upgrade(
        self,
        record: UpgradeRecord,
    ) -> bool:
        """
        Validate and record an upgrade.
        """

        if not self.validator.validate(record):
            return False

        self.records.append(record)
        return True

    def latest(self) -> UpgradeRecord:
        """
        Return the most recent upgrade.
        """

        if not self.records:
            raise ValueError(
                "No upgrades recorded."
            )

        return self.records[-1]

    def count(self) -> int:
        """
        Return the number of recorded upgrades.
        """

        return len(self.records)