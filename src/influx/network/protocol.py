from __future__ import annotations

from influx.network.message import NetworkMessage


class NetworkProtocol:
    """
    Base deterministic network protocol.
    """

    VERSION = "1.0"

    def validate(
        self,
        message: NetworkMessage,
    ) -> bool:
        """
        Validate incoming message.
        """

        message.validate()

        return True