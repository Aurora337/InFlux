from __future__ import annotations

from .gossip_message import GossipMessage
from .gossip_state import GossipState


class Gossip:
    """
    Deterministic gossip engine.
    """


    def __init__(self) -> None:

        self.state = GossipState.INITIALIZING

        self.messages: list[GossipMessage] = []


    def start(
        self,
    ) -> bool:
        """
        Activate gossip subsystem.
        """

        self.state = GossipState.ACTIVE

        return True


    def propagate(
        self,
        message: GossipMessage,
    ) -> bool:
        """
        Propagate gossip message.
        """

        if self.state != GossipState.ACTIVE:
            return False

        message.increment_hop()

        self.messages.append(
            message
        )

        self.state = GossipState.PROPAGATING

        return True
    

    def receive(
        self,
        message: GossipMessage,
    ) -> bool:
        """
        Receive a gossip message.
        """

        if message.expired():
            return False

        self.messages.append(
            message
        )

        return True


    def stop(
        self,
    ) -> bool:
        """
        Stop gossip subsystem.
        """

        self.state = GossipState.STOPPED

        return True
    

    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic gossip snapshot.
        """

        return {
            "state": self.state.value,
            "messages": len(self.messages),
        }