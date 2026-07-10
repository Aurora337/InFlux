from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StateDiff:
    """
    Represents deterministic differences
    between two state snapshots.
    """

    added: dict[str, Any] = field(
        default_factory=dict
    )

    modified: dict[str, Any] = field(
        default_factory=dict
    )

    removed: list[str] = field(
        default_factory=list
    )

    def is_empty(
        self,
    ) -> bool:
        """
        Determine if no changes exist.
        """

        return (
            not self.added
            and not self.modified
            and not self.removed
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic diff snapshot.
        """

        return {
            "added":
                dict(self.added),

            "modified":
                dict(self.modified),

            "removed":
                list(self.removed),
        }


class StateDiffGenerator:
    """
    Generates deterministic state differences.
    """

    def compare(
        self,
        old_state: dict[str, Any],
        new_state: dict[str, Any],
    ) -> StateDiff:
        """
        Compare two state snapshots.
        """

        added = {}
        modified = {}
        removed = []

        for key, value in new_state.items():

            if key not in old_state:
                added[key] = value

            elif old_state[key] != value:
                modified[key] = value

        for key in old_state:

            if key not in new_state:
                removed.append(key)

        return StateDiff(
            added=added,
            modified=modified,
            removed=sorted(
                removed
            ),
        )