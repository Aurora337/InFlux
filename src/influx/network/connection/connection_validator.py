from __future__ import annotations

from dataclasses import dataclass

from influx.network.peer import Peer

from .connection import Connection
from .connection_policy import ConnectionPolicy


@dataclass
class ConnectionValidator:
    """
    Validates connection requests before acceptance.
    """

    policy: ConnectionPolicy


    def validate_peer(
        self,
        peer: Peer
    ) -> bool:
        """
        Validate peer identity.
        """

        if not peer.node_id:
            return False

        if not peer.address:
            return False

        if not (1 <=peer.port <= 65635):
            return False

        if not peer.active:
            return False

        return True


    def validate_duplicate(
        self,
        peer: Peer,
        connections: list[Connection]
    ) -> bool:
        """
        Prevent duplicate connections.
        """

        for connection in connections:
            if connection.peer.node_id == peer.node_id:
                return False

        return True


    def validate_connection(
        self,
        peer: Peer,
        connections: list[Connection]
    ) -> bool:
        """
        Full connection validation pipeline.
        """

        if not self.validate_peer(peer):
            return False


        if not self.validate_duplicate(
            peer,
            connections
        ):
            return False


        if not self.policy.allows_peer(
            peer,
            len(connections)
        ):
            return False


        return True