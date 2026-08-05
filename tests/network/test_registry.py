from influx.network.peer import Peer
from influx.network.registry import PeerRegistry
from influx.network.address import NetworkAddress


def create_peer(node_id: str) -> Peer:
    return Peer(
        node_id=node_id,
        address=NetworkAddress(
            "localhost",
            9000,
        ),
    )


def test_register_peer() -> None:
    registry = PeerRegistry()

    peer = create_peer("node-1")

    registry.register(peer)

    assert registry.get("node-1") == peer


def test_unregister_peer() -> None:
    registry = PeerRegistry()

    peer = create_peer("node-1")

    registry.register(peer)

    registry.unregister("node-1")

    assert registry.get("node-1") is None


def test_peer_count() -> None:
    registry = PeerRegistry()

    registry.register(
        create_peer("node-1")
    )

    registry.register(
        create_peer("node-2")
    )

    assert registry.count() == 2


def test_deterministic_order() -> None:
    registry = PeerRegistry()

    registry.register(
        create_peer("node-b")
    )

    registry.register(
        create_peer("node-a")
    )

    peers = registry.peers()

    assert peers[0].node_id == "node-a"
    assert peers[1].node_id == "node-b"