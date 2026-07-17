from influx.network.address import NetworkAddress
from influx.network.node.node_discovery import NodeDiscovery
from influx.network.peer import Peer
from influx.network.registry import PeerRegistry


def create_peer() -> Peer:
    return Peer(
        peer_id="peer-1",
        address=NetworkAddress(
            "127.0.0.1",
            9000,
        ),
    )


def test_discover_peer() -> None:
    discovery = NodeDiscovery(
        PeerRegistry(),
    )

    peer = create_peer()

    discovery.discover(peer)

    assert discovery.count() == 1
    assert discovery.peers()[0].peer_id == "peer-1"


def test_forget_peer() -> None:
    discovery = NodeDiscovery(
        PeerRegistry(),
    )

    peer = create_peer()

    discovery.discover(peer)

    discovery.forget("peer-1")

    assert discovery.count() == 0