from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransportMetrics:
    """
    Transport performance metrics.

    These metrics provide the foundation for future
    adaptive networking decisions.
    """

    sessions_opened: int = 0

    sessions_closed: int = 0

    send_operations: int = 0

    receive_operations: int = 0

    bytes_sent: int = 0

    bytes_received: int = 0

    failures: int = 0

    heartbeat_failures: int = 0

    latency_total: float = 0.0

    latency_samples: int = 0


    @property
    def average_latency(
        self,
    ) -> float:
        """
        Average observed latency.
        """

        if self.latency_samples == 0:
            return 0.0

        return (
            self.latency_total
            /
            self.latency_samples
        )


    def record_open(self) -> None:
        self.sessions_opened += 1


    def record_close(self) -> None:
        self.sessions_closed += 1


    def record_send(
        self,
        size: int,
    ) -> None:
        self.send_operations += 1
        self.bytes_sent += size


    def record_receive(
        self,
        size: int,
    ) -> None:
        self.receive_operations += 1
        self.bytes_received += size


    def record_failure(self) -> None:
        self.failures += 1


    def record_heartbeat_failure(self) -> None:
        self.heartbeat_failures += 1


    def record_latency(
        self,
        latency: float,
    ) -> None:
        self.latency_total += latency
        self.latency_samples += 1


    def snapshot(self) -> dict[str, int | float]:
        """
        Deterministic metrics snapshot.
        """

        return {
            "sessions_opened":
                self.sessions_opened,

            "sessions_closed":
                self.sessions_closed,

            "send_operations":
                self.send_operations,

            "receive_operations":
                self.receive_operations,

            "bytes_sent":
                self.bytes_sent,

            "bytes_received":
                self.bytes_received,

            "failures":
                self.failures,

            "heartbeat_failures":
                self.heartbeat_failures,

            "average_latency":
                self.average_latency,
        }