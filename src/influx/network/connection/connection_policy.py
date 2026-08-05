from __future__ import annotations

from dataclasses import dataclass

from influx.network.peer import Peer


@dataclass
class ConnectionPolicy:
    """
    Defines deterministic connection acceptance rules.
    """

    max_peers: int = 64

    allow_loopback: bool = False

    validator_priority: bool = True

    archive_priority: bool = True

    storage_priority: bool = True


    def allows_peer(
        self,
        peer: Peer,
        current_count: int
    ) -> bool:
        """
        Determine whether a peer may connect.
        """

        if current_count >= self.max_peers:
            return False


        if not self.allow_loopback:
            if peer.address in (
                "127.0.0.1",
                "localhost",
                "::1",
            ):
                return False


        if not peer.active:
            return False


        return True