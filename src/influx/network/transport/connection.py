from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from .connection_state import ConnectionState


@dataclass(slots=True)
class Connection:
    """
    Deterministic peer connection.
    """

    connection_id: str

    peer_id: str

    state: ConnectionState = ConnectionState.DISCONNECTED

    created_at: float = field(default_factory=time)

    last_activity: float = field(default_factory=time)

    bytes_sent: int = 0

    bytes_received: int = 0

    def connect(self) -> bool:
        if self.state == ConnectionState.CONNECTED:
            return False

        self.state = ConnectionState.CONNECTED
        self.last_activity = time()

        return True

    def disconnect(self) -> bool:
        if self.state == ConnectionState.CLOSED:
            return False

        self.state = ConnectionState.CLOSED
        self.last_activity = time()

        return True

    def record_send(
        self,
        size: int,
    ) -> None:
        self.bytes_sent += size
        self.last_activity = time()

    def record_receive(
        self,
        size: int,
    ) -> None:
        self.bytes_received += size
        self.last_activity = time()

    def snapshot(self) -> dict:
        return {
            "connection_id": self.connection_id,
            "peer_id": self.peer_id,
            "state": self.state.value,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "last_activity": self.last_activity,
        }