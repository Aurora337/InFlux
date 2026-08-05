from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SyncRequest:
    """
    Represents a state synchronization request.
    """

    height: int


class PeerSynchronizer:
    """
    Synchronizes state between peers.
    """

    def __init__(
        self,
    ) -> None:

        self._synced: dict[
            int,
            dict[str, Any],
        ] = {}

    def sync(
        self,
        request: SyncRequest,
        state: dict[str, Any],
    ) -> bool:
        """
        Store synchronized state.
        """

        self._synced[
            request.height
        ] = dict(state)

        return True

    def get(
        self,
        height: int,
    ) -> dict[str, Any] | None:
        """
        Retrieve synchronized state.
        """

        return self._synced.get(
            height
        )

    def synced_heights(
        self,
    ) -> list[int]:
        """
        Return deterministic sync history.
        """

        return sorted(
            self._synced.keys()
        )