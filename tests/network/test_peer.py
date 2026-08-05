from influx.network.address import NetworkAddress
from influx.network.errors import PeerError
from influx.network.peer import Peer

import pytest


def test_connect() -> None:
    peer = Peer(
        peer_id="peer-1",
        address=NetworkAddress(
            "localhost",
            8000,
        ),
    )

    peer.connect()

    assert peer.online


def test_disconnect() -> None:
    peer = Peer(
        peer_id="peer-1",
        address=NetworkAddress(
            "localhost",
            8000,
        ),
    )

    peer.connect()
    peer.disconnect()

    assert not peer.online


def test_is_online() -> None:
    peer = Peer(
        peer_id="peer-1",
        address=NetworkAddress(
            "localhost",
            8000,
        ),
    )

    assert not peer.is_online()

    peer.connect()

    assert peer.is_online()


def test_missing_peer_id() -> None:
    peer = Peer(
        peer_id="",
        address=NetworkAddress(
            "localhost",
            8000,
        ),
    )

    with pytest.raises(PeerError):
        peer.connect()