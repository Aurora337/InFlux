from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GossipMetrics:
    """
    Metrics for gossip propagation.
    """

    messages_received: int = 0

    messages_propagated: int = 0

    messages_rejected: int = 0

    duplicates_detected: int = 0

    expired_messages: int = 0


    def record_received(
        self,
    ) -> None:

        self.messages_received += 1


    def record_propagated(
        self,
    ) -> None:

        self.messages_propagated += 1


    def record_rejected(
        self,
    ) -> None:

        self.messages_rejected += 1


    def record_duplicate(
        self,
    ) -> None:

        self.duplicates_detected += 1


    def record_expired(
        self,
    ) -> None:

        self.expired_messages += 1


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "messages_received":
                self.messages_received,

            "messages_propagated":
                self.messages_propagated,

            "messages_rejected":
                self.messages_rejected,

            "duplicates_detected":
                self.duplicates_detected,

            "expired_messages":
                self.expired_messages,
        }