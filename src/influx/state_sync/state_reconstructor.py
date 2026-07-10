from __future__ import annotations

from typing import Any

from .state_diff import (
    StateDiff,
)


class StateReconstructor:
    """
    Reconstructs deterministic state
    from synchronization differences.
    """

    def apply(
        self,
        state: dict[str, Any],
        diff: StateDiff,
    ) -> dict[str, Any]:
        """
        Apply state changes.
        """

        reconstructed = dict(
            state
        )

        for key, value in diff.added.items():

            reconstructed[key] = value

        for key, value in diff.modified.items():

            reconstructed[key] = value

        for key in diff.removed:

            reconstructed.pop(
                key,
                None,
            )

        return reconstructed

    def verify(
        self,
        state: dict[str, Any],
        expected: dict[str, Any],
    ) -> bool:
        """
        Verify reconstructed state.
        """

        return (
            state
            ==
            expected
        )