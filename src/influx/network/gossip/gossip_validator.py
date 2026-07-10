from __future__ import annotations

from .gossip_message import GossipMessage
from .gossip_policy import GossipPolicy
from .gossip_table import GossipTable


class GossipValidator:
    """
    Validates gossip messages before admission.
    """


    def __init__(
        self,
        policy: GossipPolicy,
        table: GossipTable,
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


        if not self.policy.validate_message(
            message.ttl,
            message.hops,
            message.signature,
        ):
            return False


        if self.policy.prevent_duplicates:

            if self.table.lookup(
                message.message_id
            ):
                return False


        return True