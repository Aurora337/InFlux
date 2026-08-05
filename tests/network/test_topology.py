from influx.network.address import NetworkAddress
from influx.network.peer import Peer
from influx.network.topology import NetworkTopology


def create_peer(node_id: str) -> Peer:
    return Peer(
        node_id=node_id,
        address=NetworkAddress(
            "localhost",
            9000,
        ),
    )


def test_add_peer() -> None:
    topology = NetworkTopology()

    peer = create_peer("node-1")

    topology.add(peer)

    assert topology.peers()[0] == peer


def test_remove_peer() -> None:
    topology = NetworkTopology()

    peer = create_peer("node-1")

    topology.add(peer)

    topology.remove("node-1")

    assert topology.peers() == []


def test_multiple_peers() -> None:
    topology = NetworkTopology()

    topology.add(
        create_peer("node-2")
    )

    topology.add(
        create_peer("node-1")
    )

    peers = topology.peers()

    assert peers[0].node_id == "node-1"
    assert peers[1].node_id == "node-2"


def test_remove_unknown_peer() -> None:
    topology = NetworkTopology()

    topology.remove("missing")

    assert topology.peers() == []