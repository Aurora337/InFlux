from __future__ import annotations

from typing import Dict, Optional

from .gossip_message import GossipMessage


class GossipTable:
    """
    Stores known gossip messages.

    Prevents duplicate propagation and keeps
    deterministic message history.
    """

    def __init__(self) -> None:

        self.messages: Dict[
            str,
            GossipMessage
        ] = {}


    def add(
        self,
        message: GossipMessage,
    ) -> bool:
        """
        Add gossip message.

        Returns False if already known.
        """

        if message.message_id in self.messages:
            return False

        self.messages[
            message.message_id
        ] = message

        return True


    def lookup(
        self,
        message_id: str,
    ) -> Optional[GossipMessage]:
        """
        Retrieve known message.
        """

        return self.messages.get(
            message_id
        )


    def remove(
        self,
        message_id: str,
    ) -> bool:
        """
        Remove message.
        """

        if message_id not in self.messages:
            return False

        del self.messages[
            message_id
        ]

        return True


    def active_messages(
        self,
    ) -> list[GossipMessage]:
        """
        Return messages still eligible
        for propagation.
        """

        return [
            message
            for message in self.messages.values()
            if not message.expired()
        ]


    def count(
        self,
    ) -> int:
        """
        Return stored message count.
        """

        return len(
            self.messages
        )


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic table snapshot.
        """

        return {
            message_id:
                message.snapshot()

            for message_id, message
            in self.messages.items()
        }