from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from influx.state_root.state_root import (
    StateRoot,
)


@dataclass(slots=True)
class StateSnapshot:
    """
    Represents a deterministic state snapshot.
    """

    height: int

    state: dict[str, Any]

    root_hash: str

    @classmethod
    def create(
        cls,
        height: int,
        state: dict[str, Any],
    ) -> "StateSnapshot":
        """
        Create verified snapshot from state.
        """

        root = StateRoot(
            state
        )

        return cls(
            height=height,
            state=dict(state),
            root_hash=root.calculate(),
        )

    def verify(
        self,
    ) -> bool:
        """
        Verify snapshot integrity.
        """

        root = StateRoot(
            self.state
        )

        return (
            root.calculate()
            ==
            self.root_hash
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic snapshot output.
        """

        return {
            "height":
                self.height,

            "state":
                dict(self.state),

            "root_hash":
                self.root_hash,
        }