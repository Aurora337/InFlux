from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveryMetrics:
    """
    Metrics for peer discovery operations.
    """

    discovery_attempts: int = 0

    peers_discovered: int = 0

    peers_rejected: int = 0

    peers_removed: int = 0

    validation_failures: int = 0


    def record_attempt(
        self,
    ) -> None:
        self.discovery_attempts += 1


    def record_discovered(
        self,
    ) -> None:
        self.peers_discovered += 1


    def record_rejected(
        self,
    ) -> None:
        self.peers_rejected += 1


    def record_removed(
        self,
    ) -> None:
        self.peers_removed += 1


    def record_validation_failure(
        self,
    ) -> None:
        self.validation_failures += 1


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "discovery_attempts":
                self.discovery_attempts,

            "peers_discovered":
                self.peers_discovered,

            "peers_rejected":
                self.peers_rejected,

            "peers_removed":
                self.peers_removed,

            "validation_failures":
                self.validation_failures,
        }