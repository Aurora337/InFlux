from __future__ import annotations

from .channel import Channel
from .channel_state import ChannelState
from .connection import Connection
from .connection_state import ConnectionState


class TransportPolicy:
    """
    Deterministic transport validation policy.
    """

    def validate_connection(
        self,
        connection: Connection,
    ) -> bool:
        """
        Determine whether a connection may be used.
        """

        return (
            connection.state
            == ConnectionState.CONNECTED
        )

    def validate_channel(
        self,
        channel: Channel,
    ) -> bool:
        """
        Determine whether a channel may be used.
        """

        return (
            channel.state
            == ChannelState.OPEN
        )

    def validate(
        self,
        connection: Connection,
        channel: Channel,
    ) -> bool:
        """
        Validate a transport path.
        """

        return (
            self.validate_connection(connection)
            and self.validate_channel(channel)
        )