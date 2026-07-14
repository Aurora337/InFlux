from __future__ import annotations

from dataclasses import dataclass, field

from .snapshot import StateSnapshot


@dataclass(slots=True)
class StateHistory:
    """
    Deterministic contract state history tracker.
    """

    _snapshots: list[StateSnapshot] = field(
        default_factory=list
    )

    def add(
        self,
        snapshot: StateSnapshot,
    ) -> None:
        """
        Add a state snapshot.
        """

        self._snapshots.append(snapshot)

    def latest(
        self,
    ) -> StateSnapshot:
        """
        Return latest snapshot.
        """

        if not self._snapshots:
            raise ValueError(
                "No state history available."
            )

        return self._snapshots[-1]

    def get(
        self,
        height: int,
    ) -> StateSnapshot:
        """
        Retrieve snapshot by height.
        """

        for snapshot in self._snapshots:
            if snapshot.height == height:
                return snapshot

        raise ValueError(
            "Unknown state height."
        )

    def count(self) -> int:
        return len(self._snapshots)

    def heights(self) -> list[int]:
        """
        Return deterministic height ordering.
        """

        return [
            snapshot.height
            for snapshot in self._snapshots
        ]