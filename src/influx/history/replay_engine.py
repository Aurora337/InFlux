from __future__ import annotations

from typing import Any

from .state_history import (
    StateHistory,
)


class ReplayEngine:
    """
    Reconstructs historical states deterministically.
    """

    def __init__(
        self,
        history: StateHistory,
    ) -> None:

        self.history = history

    def replay(
        self,
        height: int,
    ) -> dict[str, Any] | None:
        """
        Replay state at historical height.
        """

        historical = self.history.get(
            height
        )

        if historical is None:
            return None

        return dict(
            historical.state
        )

    def verify(
        self,
        height: int,
        expected_root: str,
    ) -> bool:
        """
        Verify historical root.
        """

        historical = self.history.get(
            height
        )

        if historical is None:
            return False

        return (
            historical.root_hash
            ==
            expected_root
        )