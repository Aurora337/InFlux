from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NodeMetrics:
    """
    Runtime metrics for an InFlux node.

    These metrics provide observability for node
    performance, availability, and network behavior.
    """

    uptime_seconds: float = 0.0

    messages_sent: int = 0

    messages_received: int = 0

    peers_connected: int = 0

    synchronization_events: int = 0

    failures: int = 0


    def record_sent(
        self,
    ) -> None:
        """
        Record outgoing message.
        """

        self.messages_sent += 1


    def record_received(
        self,
    ) -> None:
        """
        Record incoming message.
        """

        self.messages_received += 1


    def record_peer(
        self,
        count: int,
    ) -> None:
        """
        Update connected peers.
        """

        self.peers_connected = count


    def record_sync(
        self,
    ) -> None:
        """
        Record synchronization event.
        """

        self.synchronization_events += 1


    def record_failure(
        self,
    ) -> None:
        """
        Record runtime failure.
        """

        self.failures += 1


    def snapshot(self) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "uptime_seconds":
                self.uptime_seconds,

            "messages_sent":
                self.messages_sent,

            "messages_received":
                self.messages_received,

            "peers_connected":
                self.peers_connected,

            "synchronization_events":
                self.synchronization_events,

            "failures":
                self.failures,
        }