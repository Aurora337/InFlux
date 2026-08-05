from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NetworkMetrics:
    """
    Testnet network measurements.
    """

    node_count: int

    online_nodes: int

    events_processed: int

    def availability_ratio(
        self,
    ) -> float:
        """
        Calculate node availability.
        """

        if self.node_count == 0:
            return 0.0

        return (
            self.online_nodes
            /
            self.node_count
        )