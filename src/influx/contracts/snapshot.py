from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state import ContractState


@dataclass(frozen=True, slots=True)
class ContractSnapshot:
    """
    Immutable deterministic snapshot of contract state.
    """

    values: dict[str, Any]

    @classmethod
    def create(
        cls,
        state: ContractState,
    ) -> "ContractSnapshot":
        return cls(
            values=state.snapshot(),
        )

    def restore(
        self,
        state: ContractState,
    ) -> None:
        state.restore(self.values)

    def size(self) -> int:
        return len(self.values)