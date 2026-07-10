from __future__ import annotations

from dataclasses import dataclass

from .state_root import StateRoot


@dataclass(slots=True)
class StateCommitment:
    """
    Represents a deterministic state commitment.
    """

    height: int

    root_hash: str

    state_size: int

    @classmethod
    def from_state(
        cls,
        height: int,
        state: dict[str, object],
    ) -> "StateCommitment":
        """
        Create commitment from state.
        """

        root = StateRoot(
            state
        )

        return cls(
            height=height,
            root_hash=root.calculate(),
            state_size=len(state),
        )

    def verify(
        self,
        state: dict[str, object],
    ) -> bool:
        """
        Verify state matches commitment.
        """

        root = StateRoot(
            state
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
        Deterministic commitment snapshot.
        """

        return {
            "height":
                self.height,

            "root_hash":
                self.root_hash,

            "state_size":
                self.state_size,
        }