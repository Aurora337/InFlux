from __future__ import annotations

from dataclasses import dataclass, field

from .snapshot import ContractSnapshot
from .state import ContractState


@dataclass(slots=True)
class ContractCheckpointManager:
    """
    Deterministic checkpoint manager.
    """

    _checkpoints: dict[str, ContractSnapshot] = field(default_factory=dict)

    def create(
        self,
        name: str,
        state: ContractState,
    ) -> None:
        self._checkpoints[name] = ContractSnapshot.create(state)

    def restore(
        self,
        name: str,
        state: ContractState,
    ) -> None:
        self._checkpoints[name].restore(state)

    def exists(
        self,
        name: str,
    ) -> bool:
        return name in self._checkpoints

    def count(self) -> int:
        return len(self._checkpoints)

    def names(self) -> list[str]:
        return sorted(self._checkpoints.keys())