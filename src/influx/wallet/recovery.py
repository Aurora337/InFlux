from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RecoveryRecord:
    """
    Represents wallet recovery information.
    """

    account_id: str

    recovery_key: str

    created_at: int

    active: bool = True

    def revoke(
        self,
    ) -> None:
        """
        Disable recovery record.
        """

        self.active = False

    def restore(
        self,
    ) -> None:
        """
        Reactivate recovery record.
        """

        self.active = True


class RecoveryManager:
    """
    Handles wallet recovery records.
    """

    def __init__(
        self,
    ) -> None:

        self._records: dict[
            str,
            RecoveryRecord,
        ] = {}

    def create(
        self,
        account_id: str,
        recovery_key: str,
        created_at: int,
    ) -> RecoveryRecord:
        """
        Create recovery record.
        """

        record = RecoveryRecord(
            account_id=account_id,
            recovery_key=recovery_key,
            created_at=created_at,
        )

        self._records[
            account_id
        ] = record

        return record

    def get(
        self,
        account_id: str,
    ) -> RecoveryRecord | None:
        """
        Retrieve recovery record.
        """

        return self._records.get(
            account_id
        )

    def remove(
        self,
        account_id: str,
    ) -> bool:
        """
        Remove recovery record.
        """

        if account_id in self._records:

            del self._records[
                account_id
            ]

            return True

        return False