from __future__ import annotations

from typing import Dict, Optional

from .discovery import Discovery
from .discovery_record import DiscoveryRecord


class DiscoveryManager:
    """
    Controls discovery instances.

    Supports simulations and multi-network
    environments where multiple discovery
    domains may exist.
    """

    def __init__(self) -> None:

        self.instances: Dict[
            str,
            Discovery,
        ] = {}


    def register(
        self,
        name: str,
        discovery: Discovery,
    ) -> None:
        """
        Register discovery service.
        """

        self.instances[name] = discovery


    def lookup(
        self,
        name: str,
    ) -> Optional[Discovery]:
        """
        Retrieve discovery service.
        """

        return self.instances.get(
            name
        )


    def discover(
        self,
        name: str,
        record: DiscoveryRecord,
    ) -> bool:
        """
        Discover peer through service.
        """

        discovery = self.lookup(
            name
        )

        if discovery is None:
            return False

        return discovery.discover(
            record
        )


    def start_all(self) -> None:
        """
        Start discovery services.
        """

        for discovery in self.instances.values():

            discovery.start()


    def stop_all(self) -> None:
        """
        Stop discovery services.
        """

        for discovery in self.instances.values():

            discovery.stop()


    def snapshot(self) -> dict:
        """
        Deterministic manager snapshot.
        """

        return {
            name:
                discovery.snapshot()

            for name, discovery
            in self.instances.items()
        }