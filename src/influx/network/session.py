from __future__ import annotations

from dataclasses import dataclass

from influx.network.peer import Peer


@dataclass
class NetworkSession:
    """
    Represents an active deterministic session with a peer.
    """

    peer: Peer

    connected: bool = False

    messages_sent: int = 0

    messages_received: int = 0

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def record_sent(self) -> None:
        self.messages_sent += 1

    def record_received(self) -> None:
        self.messages_received += 1