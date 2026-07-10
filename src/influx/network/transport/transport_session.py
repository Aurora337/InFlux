from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any

from .transport_type import TransportType


@dataclass(slots=True)
class TransportSession:
    """
    Represents one active transport communication session.

    Sessions track the lifecycle of communication between
    local and remote nodes without knowing the underlying
    transport implementation.
    """

    session_id: str

    peer_id: str

    transport_type: TransportType

    connected: bool = False

    created_at: float = field(
        default_factory=time
    )

    last_activity: float = field(
        default_factory=time
    )

    bytes_sent: int = 0

    bytes_received: int = 0

    latency: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    def open(self) -> None:
        """
        Activate session.
        """

        self.connected = True

        self.last_activity = time()


    def close(self) -> None:
        """
        Close session.
        """

        self.connected = False

        self.last_activity = time()


    def touch(self) -> None:
        """
        Update session activity.
        """

        self.last_activity = time()


    def record_send(
        self,
        size: int,
    ) -> None:
        """
        Record outgoing bytes.
        """

        self.bytes_sent += size

        self.touch()


    def record_receive(
        self,
        size: int,
    ) -> None:
        """
        Record incoming bytes.
        """

        self.bytes_received += size

        self.touch()


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic session snapshot.
        """

        return {
            "session_id":
                self.session_id,

            "peer_id":
                self.peer_id,

            "transport_type":
                self.transport_type.value,

            "connected":
                self.connected,

            "created_at":
                self.created_at,

            "last_activity":
                self.last_activity,

            "bytes_sent":
                self.bytes_sent,

            "bytes_received":
                self.bytes_received,

            "latency":
                self.latency,

            "metadata":
                dict(self.metadata),
        }