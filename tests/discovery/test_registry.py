import pytest

from influx.discovery.registry import (
    PeerRecord,
    PeerRegistry,
)

from influx.discovery.exceptions import (
    InvalidPeerError,
    PeerNotFoundError,
)


def test_register_peer():

    registry = PeerRegistry()

    peer = PeerRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8000,
    )

    registry.register(peer)

    assert (
        registry.exists("node-1")
        is True
    )


def test_get_peer():

    registry = PeerRegistry()

    peer = PeerRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8000,
    )

    registry.register(peer)

    result = registry.get(
        "node-1"
    )

    assert (
        result
        == peer
    )


def test_remove_peer():

    registry = PeerRegistry()

    peer = PeerRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8000,
    )

    registry.register(peer)

    removed = registry.remove(
        "node-1"
    )

    assert removed is True

    assert (
        registry.exists(
            "node-1"
        )
        is False
    )


def test_missing_peer():

    registry = PeerRegistry()

    with pytest.raises(
        PeerNotFoundError
    ):

        registry.get(
            "unknown"
        )


def test_invalid_peer():

    registry = PeerRegistry()

    peer = PeerRecord(
        node_id="",
        address="127.0.0.1",
        port=8000,
    )

    with pytest.raises(
        InvalidPeerError
    ):

        registry.register(
            peer
        )


def test_peer_count():

    registry = PeerRegistry()

    registry.register(
        PeerRecord(
            node_id="node-1",
            address="127.0.0.1",
            port=8000,
        )
    )

    assert (
        registry.count()
        == 1
    )