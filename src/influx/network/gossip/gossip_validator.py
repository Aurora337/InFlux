from __future__ import annotations

from .gossip_message import GossipMessage


class GossipValidator:
    """
    Validates gossip messages.
    """


    def __init__(
        self,
        policy=None,
        table=None,
    ) -> None:

        self.policy = policy

        self.table = table


    def validate(
        self,
        message: GossipMessage,
    ) -> bool:
        """
        Validate gossip message.
        """

        if not message.origin:
            return False

        if not message.signature:
            return False

        if message.expired():
            return False

        return True