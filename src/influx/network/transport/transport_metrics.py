from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransportMetrics:
    """
    Deterministic transport metrics tracker.

    Tracks transport lifecycle, traffic volume,
    operations, failures, and latency.
    """

    # Session lifecycle

    sessions_opened: int = 0

    sessions_closed: int = 0


    # Traffic

    bytes_sent: int = 0

    bytes_received: int = 0


    # Operations

    send_operations: int = 0

    receive_operations: int = 0


    # Health

    failures: int = 0

    heartbeat_failures: int = 0


    # Performance

    latency_total: float = 0.0

    latency_samples: int = 0


    def record_open(
        self,
    ) -> None:
        """
        Record session opening.
        """

        self.sessions_opened += 1


    def record_close(
        self,
    ) -> None:
        """
        Record session closing.
        """

        self.sessions_closed += 1


    def record_send(
        self,
        size: int = 0,
    ) -> None:
        """
        Record sent bytes.
        """

        self.send_operations += 1
        self.bytes_sent += size


    def record_receive(
        self,
        size: int = 0,
    ) -> None:
        """
        Record received bytes.
        """

        self.receive_operations += 1
        self.bytes_received += size


    def record_failure(
        self,
    ) -> None:
        """
        Record transport failure.
        """

        self.failures += 1


    def record_heartbeat_failure(
        self,
    ) -> None:
        """
        Record heartbeat failure.
        """

        self.heartbeat_failures += 1


    def record_latency(
        self,
        latency: float,
    ) -> None:
        """
        Record latency sample.
        """

        self.latency_total += latency
        self.latency_samples += 1


    @property
    def average_latency(
        self,
    ) -> float:
        """
        Return average latency.
        """

        if self.latency_samples == 0:
            return 0.0

        return (
             self.latency_total
             /
             self.latency_samples
        )


    def snapshot(self) -> dict:
        return {
            "sessions_opened": self.sessions_opened,
            "sessions_closed": self.sessions_closed,

            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,

            "send_operations": self.send_operations,
            "receive_operations": self.receive_operations,

            "messages_sent": self.send_operations,
            "messages_received": self.receive_operations,

            "failures": self.failures,
            "heartbeat_failures": self.heartbeat_failures,

            "average_latency": self.average_latency,
        }