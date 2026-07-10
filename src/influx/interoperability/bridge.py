from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BridgeConnection:
    """
    Represents a connection between networks.
    """

    source_network: str

    destination_network: str

    active: bool = True


class InteroperabilityBridge:
    """
    Manages deterministic cross-network connections.
    """

    def __init__(
        self,
    ) -> None:

        self._connections: list[BridgeConnection] = []

    def connect(
        self,
        source_network: str,
        destination_network: str,
    ) -> BridgeConnection:
        """
        Create a network bridge.
        """

        connection = BridgeConnection(
            source_network=source_network,
            destination_network=destination_network,
        )

        self._connections.append(
            connection
        )

        return connection

    def connections(
        self,
    ) -> list[BridgeConnection]:
        """
        Return active bridge connections.
        """

        return list(
            self._connections
        )