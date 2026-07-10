from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class HistoricalState:
    """
    Represents a state recorded at a specific height.
    """

    height: int

    state: dict[str, Any]

    root_hash: str


class StateHistory:
    """
    Maintains deterministic historical states.
    """

    def __init__(
        self,
    ) -> None:

        self._history: dict[
            int,
            HistoricalState,
        ] = {}

    def record(
        self,
        height: int,
        state: dict[str, Any],
        root_hash: str,
    ) -> HistoricalState:
        """
        Record a historical state.
        """

        historical = HistoricalState(
            height=height,
            state=dict(state),
            root_hash=root_hash,
        )

        self._history[
            height
        ] = historical

        return historical

    def get(
        self,
        height: int,
    ) -> HistoricalState | None:
        """
        Retrieve state by height.
        """

        return self._history.get(
            height
        )

    def latest(
        self,
    ) -> HistoricalState | None:
        """
        Retrieve latest historical state.
        """

        if not self._history:
            return None

        height = max(
            self._history.keys()
        )

        return self._history[
            height
        ]

    def heights(
        self,
    ) -> list[int]:
        """
        Return deterministic height list.
        """

        return sorted(
            self._history.keys()
        )