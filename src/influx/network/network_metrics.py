from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NetworkMetrics:
    """
    Deterministic network-wide metrics.
    """

    peers_connected: int = 0
    peers_disconnected: int = 0

    messages_routed: int = 0
    messages_dropped: int = 0

    sync_rounds: int = 0
    replication_rounds: int = 0

    def record_peer_connected(self) -> None:
        self.peers_connected += 1

    def record_peer_disconnected(self) -> None:
        self.peers_disconnected += 1

    def record_route(self) -> None:
        self.messages_routed += 1

    def record_drop(self) -> None:
        self.messages_dropped += 1

    def record_sync(self) -> None:
        self.sync_rounds += 1

    def record_replication(self) -> None:
        self.replication_rounds += 1

    def snapshot(self) -> dict[str, int]:
        return {
            "peers_connected": self.peers_connected,
            "peers_disconnected": self.peers_disconnected,
            "messages_routed": self.messages_routed,
            "messages_dropped": self.messages_dropped,
            "sync_rounds": self.sync_rounds,
            "replication_rounds": self.replication_rounds,
        }