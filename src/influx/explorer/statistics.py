from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExplorerStatistics:
    """
    Explorer network statistics.
    """

    block_count: int

    transaction_count: int

    account_count: int

    def total_records(
        self,
    ) -> int:
        """
        Return total indexed records.
        """

        return (
            self.block_count
            +
            self.transaction_count
            +
            self.account_count
        )