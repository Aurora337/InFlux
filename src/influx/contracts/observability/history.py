from __future__ import annotations

from dataclasses import dataclass, field

from .record import ContractExecutionRecord


@dataclass(slots=True)
class ContractExecutionHistory:
    """
    Deterministic contract execution history.
    """

    records: list[ContractExecutionRecord] = field(
        default_factory=list,
    )

    def add(
        self,
        record: ContractExecutionRecord,
    ) -> None:
        """
        Add execution record.
        """
        self.records.append(record)

    def count(self) -> int:
        """
        Return number of records.
        """
        return len(self.records)

    def get(
        self,
        record_id: str,
    ) -> ContractExecutionRecord | None:
        """
        Retrieve record by identifier.
        """

        for record in self.records:
            if record.record_id == record_id:
                return record

        return None

    def ordered(
        self,
    ) -> list[ContractExecutionRecord]:
        """
        Return deterministic sequence ordering.
        """

        return sorted(
            self.records,
            key=lambda record: (
                record.sequence,
                record.record_id,
            ),
        )

    def clear(self) -> None:
        """
        Remove all records.
        """
        self.records.clear()