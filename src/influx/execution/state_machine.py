from __future__ import annotations

from typing import Any


class StateMachine:
    """
    Deterministic application state machine.
    """

    def __init__(
        self,
        initial_state: dict[str, Any] | None = None,
    ) -> None:

        self.state = (
            initial_state.copy()
            if initial_state is not None
            else {}
        )

    def get(
        self,
        key: str,
    ) -> Any | None:
        """
        Retrieve state value.
        """

        return self.state.get(
            key
        )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Apply deterministic state update.
        """

        self.state[key] = value

    def apply_changes(
        self,
        changes: dict[str, Any],
    ) -> None:
        """
        Apply execution changes.
        """

        for key, value in changes.items():

            self.set(
                key,
                value,
            )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic state snapshot.
        """

        return dict(
            self.state
        )