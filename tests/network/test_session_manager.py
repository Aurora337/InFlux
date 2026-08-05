from influx.network.address import NetworkAddress
from influx.network.peer import Peer
from influx.network.session_manager import SessionManager


def create_peer(node_id: str) -> Peer:
    return Peer(
        node_id=node_id,
        address=NetworkAddress(
            "localhost",
            9000,
        ),
    )


def test_open_session() -> None:
    manager = SessionManager()

    peer = create_peer(
        "node-1"
    )

    session = manager.open(peer)

    assert session is not None
    assert manager.get("node-1") is session


def test_close_session() -> None:
    manager = SessionManager()

    peer = create_peer(
        "node-1"
    )

    manager.open(peer)

    manager.close(
        "node-1"
    )

    session = manager.get(
        "node-1"
    )

    assert session is not None


def test_multiple_sessions() -> None:
    manager = SessionManager()

    manager.open(
        create_peer("node-a")
    )

    manager.open(
        create_peer("node-b")
    )

    sessions = manager.sessions()

    assert len(sessions) == 2
    assert sessions[0].peer.node_id == "node-a"
    assert sessions[1].peer.node_id == "node-b"