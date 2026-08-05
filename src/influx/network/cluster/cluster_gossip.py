from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterGossip:
    """
    Tracks deterministic gossip propagation.
    """

    messages_sent: int = 0

    messages_received: int = 0

    def send(self) -> None:
        self.messages_sent += 1

    def receive(self) -> None:
        self.messages_received += 1

    def snapshot(
        self,
    ) -> dict[str, int]:
        return {
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
        }