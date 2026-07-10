from __future__ import annotations

from influx.network.message import NetworkMessage


class NetworkProtocol:
    """
    Base deterministic protocol.
    """

    VERSION = "1.0"

    def validate(self, message: NetworkMessage) -> bool:
        return message.message_id != ""