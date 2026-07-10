from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from influx.network.transport import TransportType


@dataclass(slots=True)
class NodeConfig:
    """
    Configuration for an InFlux node runtime.

    Keeps operational choices separate from
    node identity and runtime state.
    """

    node_name: str = "influx-node"

    max_peers: int = 64

    enable_sync: bool = True

    enable_consensus: bool = True

    transport: TransportType = (
        TransportType.LOCAL
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    def validate(self) -> bool:
        """
        Validate node configuration.
        """

        if self.max_peers <= 0:
            return False

        return True


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic configuration snapshot.
        """

        return {
            "node_name": self.node_name,
            "max_peers": self.max_peers,
            "enable_sync": self.enable_sync,
            "enable_consensus": self.enable_consensus,
            "transport": self.transport.value,
            "metadata": dict(self.metadata),
        }