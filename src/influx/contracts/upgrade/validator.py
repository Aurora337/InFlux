from __future__ import annotations

from dataclasses import dataclass

from .record import UpgradeRecord


@dataclass(slots=True)
class UpgradeValidator:
    """
    Deterministic contract upgrade validator.
    """

    def validate(
        self,
        record: UpgradeRecord,
    ) -> bool:
        """
        Validate an upgrade record.
        """

        if not record.contract_id:
            return False

        if not record.previous_version:
            return False

        if not record.new_version:
            return False

        if not record.migration_id:
            return False

        if not record.is_upgrade():
            return False

        return True