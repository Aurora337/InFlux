from __future__ import annotations

from influx.network.message import NetworkMessage
from influx.network.registry import PeerRegistry


class MessageRouter:
    """
    Deterministic message routing layer.
    """

    def __init__(self, registry: PeerRegistry):
        self.registry = registry

    def route(self, message: NetworkMessage) -> bool:
        """
        Route a message if the destination peer exists.
        """

        peer = self.registry.get(message.receiver_id)

        return peer is not None