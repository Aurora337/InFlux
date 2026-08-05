from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CrossNetworkState:
    """
    Represents verified state exchanged between networks.
    """

    network_id: str

    state_root: str

    height: int


class StateVerifier:
    """
    Validates cross-network state information.
    """

    def verify(
        self,
        state: CrossNetworkState,
        expected_height: int,
    ) -> bool:
        """
        Verify state consistency.
        """

        return (
            state.height
            == expected_height
        )