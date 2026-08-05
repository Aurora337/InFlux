from influx.network.transport.transport_session import (
    TransportSession,
)
from influx.network.transport.transport_type import (
    TransportType,
)


def create_session():
    return TransportSession(
        session_id="session-1",
        peer_id="node-1",
        transport_type=TransportType.TCP,
    )


def test_session_creation():

    session = create_session()

    assert session.session_id == "session-1"
    assert session.peer_id == "node-1"


def test_session_connected():

    session = create_session()

    session.connected = True

    assert session.connected


def test_session_disconnected():

    session = create_session()

    session.connected = True
    session.connected = False

    assert not session.connected


def test_session_snapshot():

    session = create_session()

    snapshot = session.snapshot()

    assert snapshot["session_id"] == "session-1"
    assert snapshot["transport_type"] == "tcp"
