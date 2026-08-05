from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NodeMetrics:
    """
    Deterministic node metrics.
    """

    messages_sent: int = 0

    messages_received: int = 0

    peers_connected: int = 0

    synchronization_events: int = 0

    errors: int = 0

    uptime_seconds: int = 0

    def record_send(self) -> None:
        self.messages_sent += 1

    def record_receive(self) -> None:
        self.messages_received += 1

    def peer_connected(self) -> None:
        self.peers_connected += 1

    def peer_disconnected(self) -> None:
        if self.peers_connected > 0:
            self.peers_connected -= 1

    def synchronized(self) -> None:
        self.synchronization_events += 1

    def record_error(self) -> None:
        self.errors += 1

    def tick(self) -> None:
        self.uptime_seconds += 1

    def snapshot(self) -> dict[str, int]:
        return {
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "peers_connected": self.peers_connected,
            "synchronization_events": self.synchronization_events,
            "errors": self.errors,
            "uptime_seconds": self.uptime_seconds,
        }