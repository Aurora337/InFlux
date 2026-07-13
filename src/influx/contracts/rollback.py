from __future__ import annotations

from dataclasses import dataclass

from .checkpoint import ContractCheckpointManager
from .state import ContractState


@dataclass(slots=True)
class ContractRollbackManager:
    """
    Deterministic contract rollback manager.
    """

    checkpoints: ContractCheckpointManager

    def rollback(
        self,
        checkpoint_name: str,
        state: ContractState,
    ) -> None:
        if not self.checkpoints.exists(checkpoint_name):
            raise ValueError(
                f"Unknown checkpoint: {checkpoint_name}"
            )

        self.checkpoints.restore(
            checkpoint_name,
            state,
        )

    def can_rollback(
        self,
        checkpoint_name: str,
    ) -> bool:
        return self.checkpoints.exists(checkpoint_name)