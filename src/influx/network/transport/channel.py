from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from .channel_state import ChannelState


@dataclass(slots=True)
class Channel:
    """
    Deterministic logical transport channel.
    """

    channel_id: str

    state: ChannelState = ChannelState.CLOSED

    created_at: float = field(default_factory=time)

    message_count: int = 0

    def open(self) -> bool:
        if self.state == ChannelState.OPEN:
            return False

        self.state = ChannelState.OPEN

        return True

    def close(self) -> bool:
        if self.state == ChannelState.CLOSED:
            return False

        self.state = ChannelState.CLOSED

        return True

    def record_message(self) -> None:
        self.message_count += 1

    def snapshot(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "state": self.state.value,
            "message_count": self.message_count,
        }