from __future__ import annotations

import time
from typing import Any, Dict

from influx.network.peer import Peer

from .connection_state import ConnectionState


class Connection:
    """
    Represents one active network connection between nodes.
    """

    def __init__(self, connection_id: str, peer: Peer) -> None:
        self.connection_id = connection_id
        self.peer = peer

        self.connected = False

        self.created_at = time.time()
        self.last_activity = self.created_at

        self.bytes_sent = 0
        self.bytes_received = 0

        self.latency = 0.0

        self.status = ConnectionState.DISCONNECTED


    def connect(self) -> None:
        """
        Establish connection.
        """

        self.status = ConnectionState.CONNECTING

        self.connected = True
        self.status = ConnectionState.CONNECTED

        self.last_activity = time.time()


    def disconnect(self) -> None:
        """
        Close connection.
        """

        self.connected = False
        self.status = ConnectionState.CLOSED

        self.last_activity = time.time()


    def heartbeat(self) -> bool:
        """
        Update connection activity timestamp.

        Returns:
            True if connection is alive.
        """

        if not self.connected:
            return False

        self.last_activity = time.time()

        return True


    def send(self, data: bytes) -> None:
        """
        Record outgoing traffic.
        """

        if not self.connected:
            raise RuntimeError(
                "Cannot send on disconnected connection"
            )

        self.bytes_sent += len(data)

        self.last_activity = time.time()


    def receive(self, data: bytes) -> None:
        """
        Record incoming traffic.
        """

        if not self.connected:
            raise RuntimeError(
                "Cannot receive on disconnected connection"
            )

        self.bytes_received += len(data)

        self.last_activity = time.time()


    def snapshot(self) -> Dict[str, Any]:
        """
        Deterministic connection state snapshot.
        """

        return {
            "connection_id": self.connection_id,
            "peer": self.peer.node_id,
            "connected": self.connected,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "latency": self.latency,
            "status": self.status.value,
        }