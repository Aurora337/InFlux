from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RecoveryState:
    """
    Represents validator recovery status.
    """

    validator_id: str

    recovered: bool = False


class RecoveryManager:
    """
    Handles validator recovery workflows.
    """

    def __init__(
        self,
    ) -> None:

        self._states: dict[
            str,
            RecoveryState,
        ] = {}

    def begin(
        self,
        validator_id: str,
    ) -> RecoveryState:
        """
        Start recovery process.
        """

        state = RecoveryState(
            validator_id=validator_id,
        )

        self._states[
            validator_id
        ] = state

        return state

    def recover(
        self,
        validator_id: str,
    ) -> bool:
        """
        Mark validator recovered.
        """

        state = self._states.get(
            validator_id
        )

        if state is None:
            return False

        state.recovered = True

        return True

    def status(
        self,
        validator_id: str,
    ) -> RecoveryState | None:
        """
        Retrieve recovery state.
        """

        return self._states.get(
            validator_id
        )