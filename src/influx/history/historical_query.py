from __future__ import annotations

from typing import Any

from .state_history import (
    StateHistory,
)


class HistoricalQuery:
    """
    Provides read-only historical state queries.
    """

    def __init__(
        self,
        history: StateHistory,
    ) -> None:

        self.history = history

    def state_at(
        self,
        height: int,
    ) -> dict[str, Any] | None:
        """
        Retrieve historical state.
        """

        historical = self.history.get(
            height
        )

        if historical is None:
            return None

        return dict(
            historical.state
        )

    def root_at(
        self,
        height: int,
    ) -> str | None:
        """
        Retrieve historical state root.
        """

        historical = self.history.get(
            height
        )

        if historical is None:
            return None

        return historical.root_hash

    def exists(
        self,
        height: int,
    ) -> bool:
        """
        Check historical availability.
        """

        return (
            self.history.get(
                height
            )
            is not None
        )