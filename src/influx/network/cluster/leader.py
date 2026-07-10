from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass(slots=True)
class Leader:
    """
    Represents the current cluster leader.
    """

    node_id: str

    elected_at: float = time()

    active: bool = True


    def deactivate(
        self,
    ) -> None:
        """
        Remove leadership status.
        """

        self.active = False


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic leader snapshot.
        """

        return {
            "node_id":
                self.node_id,

            "elected_at":
                self.elected_at,

            "active":
                self.active,
        }