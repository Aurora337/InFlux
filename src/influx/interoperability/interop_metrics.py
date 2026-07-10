from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InteropMetrics:
    """
    Tracks interoperability activity.
    """

    bridges_created: int = 0

    messages_sent: int = 0

    messages_received: int = 0

    states_verified: int = 0

    verification_failures: int = 0

    def record_bridge(
        self,
    ) -> None:
        """
        Record bridge creation.
        """

        self.bridges_created += 1

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

    def record_state_verified(
        self,
    ) -> None:
        """
        Record successful state verification.
        """

        self.states_verified += 1

    def record_verification_failure(
        self,
    ) -> None:
        """
        Record failed verification.
        """

        self.verification_failures += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Return deterministic interoperability metrics.
        """

        return {
            "bridges_created":
                self.bridges_created,

            "messages_sent":
                self.messages_sent,

            "messages_received":
                self.messages_received,

            "states_verified":
                self.states_verified,

            "verification_failures":
                self.verification_failures,
        }