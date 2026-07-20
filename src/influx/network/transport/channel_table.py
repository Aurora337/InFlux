from __future__ import annotations

from .channel import Channel
from .channel_state import ChannelState


class ChannelTable:
    """
    Deterministic registry of transport channels.
    """

    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {}

    def add(
        self,
        channel: Channel,
    ) -> bool:
        """
        Register a channel.
        """

        if channel.channel_id in self._channels:
            return False

        self._channels[
            channel.channel_id
        ] = channel

        return True

    def remove(
        self,
        channel_id: str,
    ) -> bool:
        """
        Remove a channel.
        """

        if channel_id not in self._channels:
            return False

        del self._channels[
            channel_id
        ]

        return True

    def lookup(
        self,
        channel_id: str,
    ) -> Channel | None:
        """
        Lookup a channel.
        """

        return self._channels.get(
            channel_id
        )

    def open_channels(
        self,
    ) -> list[Channel]:
        """
        Return open channels.
        """

        return [
            channel
            for channel in self._channels.values()
            if channel.state == ChannelState.OPEN
        ]

    def count(
        self,
    ) -> int:
        """
        Number of registered channels.
        """

        return len(self._channels)

    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic snapshot.
        """

        return {
            channel_id: channel.snapshot()
            for channel_id, channel
            in self._channels.items()
        }