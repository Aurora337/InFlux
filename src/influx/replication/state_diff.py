from __future__ import annotations

from typing import Any


class StateDiff:
    """
    Produces deterministic state differences.
    """

    @staticmethod
    def compare(
        old_state: dict[str, Any],
        new_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Return the deterministic difference between two states.
        """

        diff: dict[str, Any] = {}

        keys = sorted(
            set(old_state.keys()) | set(new_state.keys())
        )

        for key in keys:

            old_value = old_state.get(key)

            new_value = new_state.get(key)

            if old_value != new_value:

                diff[key] = {
                    "old": old_value,
                    "new": new_value,
                }

        return diff

    @staticmethod
    def apply(
        state: dict[str, Any],
        diff: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Apply a deterministic diff.
        """

        updated = dict(state)

        for key in sorted(diff.keys()):

            updated[key] = diff[key]["new"]

        return updated

    @staticmethod
    def is_empty(
        diff: dict[str, Any],
    ) -> bool:
        """
        Return True if no changes exist.
        """

        return len(diff) == 0