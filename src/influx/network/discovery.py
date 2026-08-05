from influx.network.peer import Peer
from influx.network.registry import PeerRegistry


class DiscoveryService:
    """
    Deterministic peer discovery.
    """

    def __init__(self, registry: PeerRegistry):
        self.registry = registry

    def announce(self, peer: Peer) -> None:
        self.registry.register(peer)

    def discover(self) -> list[Peer]:
        return self.registry.peers()