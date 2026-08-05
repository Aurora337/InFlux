from influx.discovery.registry import (
    PeerRecord,
    PeerRegistry,
)

from influx.discovery.peer_exchange import (
    PeerExchange,
)


def test_announce_peer():

    registry = PeerRegistry()

    exchange = PeerExchange(
        registry
    )

    peer = PeerRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8000,
    )

    exchange.announce(
        peer
    )

    assert (
        registry.exists(
            "node-1"
        )
        is True
    )


def test_share_peers():

    registry = PeerRegistry()

    exchange = PeerExchange(
        registry
    )

    exchange.announce(
        PeerRecord(
            node_id="node-1",
            address="127.0.0.1",
            port=8000,
        )
    )

    peers = exchange.share()

    assert len(
        peers
    ) == 1

    assert (
        peers[0].node_id
        == "node-1"
    )


def test_merge_peers():

    registry = PeerRegistry()

    exchange = PeerExchange(
        registry
    )

    peers = [
        PeerRecord(
            node_id="node-1",
            address="127.0.0.1",
            port=8000,
        ),
        PeerRecord(
            node_id="node-2",
            address="127.0.0.2",
            port=8001,
        ),
    ]

    exchange.merge(
        peers
    )

    assert (
        registry.count()
        == 2
    )