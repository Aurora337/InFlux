from __future__ import annotations

from typing import Dict, Optional

from .gossip import Gossip
from .gossip_message import GossipMessage


class GossipManager:
    """
    Manages multiple gossip domains.

    Useful for simulations, testing,
    and future network segmentation.
    """

    def __init__(self) -> None:

        self.instances: Dict[
            str,
            Gossip,
        ] = {}


    def register(
        self,
        name: str,
        gossip: Gossip,
    ) -> None:
        """
        Register gossip instance.
        """

        self.instances[name] = gossip


    def lookup(
        self,
        name: str,
    ) -> Optional[Gossip]:
        """
        Find gossip instance.
        """

        return self.instances.get(
            name
        )


    def receive(
        self,
        name: str,
        message: GossipMessage,
    ) -> bool:
        """
        Receive message through domain.
        """

        gossip = self.lookup(
            name
        )

        if gossip is None:
            return False

        return gossip.receive(
            message
        )


    def start_all(self) -> None:
        """
        Start all gossip services.
        """

        for gossip in self.instances.values():

            gossip.start()


    def stop_all(self) -> None:
        """
        Stop all gossip services.
        """

        for gossip in self.instances.values():

            gossip.stop()


    def snapshot(self) -> dict:
        """
        Deterministic manager snapshot.
        """

        return {
            name:
                gossip.snapshot()

            for name, gossip
            in self.instances.items()
        }