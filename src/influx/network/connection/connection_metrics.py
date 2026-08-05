from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConnectionMetrics:
    """
    Tracks deterministic network connection statistics.
    """

    connections_opened: int = 0

    connections_closed: int = 0

    active_connections: int = 0

    failed_connections: int = 0

    reconnections: int = 0

    total_latency: float = 0.0

    latency_samples: int = 0

    bytes_sent: int = 0

    bytes_received: int = 0

    heartbeat_failures: int = 0


    @property
    def average_latency(self) -> float:
        """
        Calculate deterministic average latency.
        """

        if self.latency_samples == 0:
            return 0.0

        return (
            self.total_latency /
            self.latency_samples
        )


    def record_open(self) -> None:
        self.connections_opened += 1
        self.active_connections += 1


    def record_close(self) -> None:
        self.connections_closed += 1

        if self.active_connections > 0:
            self.active_connections -= 1


    def record_failure(self) -> None:
        self.failed_connections += 1


    def record_reconnect(self) -> None:
        self.reconnections += 1


    def record_latency(self, latency: float) -> None:
        self.total_latency += latency
        self.latency_samples += 1


    def record_sent(self, amount: int) -> None:
        self.bytes_sent += amount


    def record_received(self, amount: int) -> None:
        self.bytes_received += amount


    def record_heartbeat_failure(self) -> None:
        self.heartbeat_failures += 1


    def snapshot(self) -> dict[str, float | int]:
        return {
            "connections_opened": self.connections_opened,
            "connections_closed": self.connections_closed,
            "active_connections": self.active_connections,
            "failed_connections": self.failed_connections,
            "reconnections": self.reconnections,
            "average_latency": self.average_latency,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "heartbeat_failures": self.heartbeat_failures,
        }