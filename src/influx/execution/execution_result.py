from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionResult:
    """
    Represents the deterministic result
    of transaction execution.
    """

    success: bool

    transaction_id: str

    state_changes: dict[str, Any] = field(
        default_factory=dict
    )

    error: str | None = None

    gas_used: int = 0

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic execution snapshot.
        """

        return {
            "success":
                self.success,

            "transaction_id":
                self.transaction_id,

            "state_changes":
                dict(self.state_changes),

            "error":
                self.error,

            "gas_used":
                self.gas_used,
        }