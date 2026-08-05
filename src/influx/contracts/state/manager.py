from __future__ import annotations

from typing import Any

from .commitment import StateCommitment
from .history import StateHistory
from .snapshot import StateSnapshot


class StateManager:
    """
    Deterministic contract state manager.
    """

    def __init__(
        self,
        history: StateHistory | None = None,
    ) -> None:
        self.history = history or StateHistory()

    def snapshot(
        self,
        contract_id: str,
        version: str,
        state: dict[str, Any],
        height: int,
    ) -> StateSnapshot:
        """
        Create and record a state snapshot.
        """

        snapshot = StateSnapshot(
            contract_id=contract_id,
            version=version,
            state=dict(state),
            height=height,
        )

        self.history.add(snapshot)

        return snapshot

    def commitment(
        self,
        snapshot: StateSnapshot,
    ) -> str:
        """
        Generate snapshot commitment.
        """

        return StateCommitment.generate(snapshot)

    def verify(
        self,
        snapshot: StateSnapshot,
        commitment: str,
    ) -> bool:
        """
        Verify snapshot integrity.
        """

        return StateCommitment.matches(
            snapshot,
            commitment,
        )

    def current(
        self,
    ) -> StateSnapshot:
        """
        Return latest state.
        """

        return self.history.latest()