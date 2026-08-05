from influx.network.transport.transport_manager import TransportManager
from influx.network.transport.transport_session import TransportSession
from influx.network.transport.transport_type import TransportType
from tests.network.transport.test_transport import MockTransport


def create_session():

    return TransportSession(
        session_id="session-1",
        peer_id="node-a",
        transport_type=TransportType.LOCAL,
    )


def test_open_session():

    manager = TransportManager(
        MockTransport()
    )

    session = create_session()

    assert manager.open(session)

    assert manager.lookup(
        "session-1"
    ) is session


def test_close_session():

    manager = TransportManager(
        MockTransport()
    )

    session = create_session()

    manager.open(session)

    assert manager.close(
        "session-1"
    )


def test_send():

    manager = TransportManager(
        MockTransport()
    )

    session = create_session()

    manager.open(session)

    assert manager.send(
        "session-1",
        b"data",
    )

    assert manager.metrics.bytes_sent == 4


def test_receive():

    manager = TransportManager(
        MockTransport()
    )

    session = create_session()

    manager.open(session)

    assert manager.receive(
        "session-1",
        b"data",
    )

    assert manager.metrics.bytes_received == 4


def test_heartbeat_all():

    manager = TransportManager(
        MockTransport()
    )

    session = create_session()

    manager.open(session)

    assert manager.heartbeat_all() == 1


def test_missing_session():

    manager = TransportManager(
        MockTransport()
    )

    assert not manager.send(
        "missing",
        b"data",
    )


def test_snapshot():

    manager = TransportManager(
        MockTransport()
    )

    snapshot = manager.snapshot()

    assert "sessions" in snapshot
    assert "metrics" in snapshot