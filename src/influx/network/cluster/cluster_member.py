from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class ClusterMember:
    """
    Represents a node participating in a cluster.
    """

    node_id: str

    address: str

    port: int

    active: bool = True

    validator: bool = False

    storage: bool = False

    archive: bool = False

    joined_at: float = field(
        default_factory=time
    )


    def activate(
        self,
    ) -> None:
        """
        Activate member.
        """

        self.active = True


    def deactivate(
        self,
    ) -> None:
        """
        Deactivate member.
        """

        self.active = False


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic member snapshot.
        """

        return {
            "node_id":
                self.node_id,

            "address":
                self.address,

            "port":
                self.port,

            "active":
                self.active,

            "validator":
                self.validator,

            "storage":
                self.storage,

            "archive":
                self.archive,

            "joined_at":
                self.joined_at,
        }