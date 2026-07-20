from influx.network.transport.transport_manager import (
    TransportManager,
)

from influx.network.transport.transport_session import (
    TransportSession,
)

from influx.network.transport.transport_type import (
    TransportType,
)


class MockTransport:

    def open(self, session):
        return True

    def close(self, session):
        return True

    def send(self, session, data):
        return True

    def receive(self, session):
        return True

    def heartbeat(self, session):
        return True


def create_manager():

    return TransportManager(
        MockTransport()
    )


def create_session():

    return TransportSession(
        session_id="session-1",
        peer_id="node-1",
        transport_type=TransportType.TCP,
    )


def test_open_session():

    manager = create_manager()

    result = manager.open(
        create_session()
    )

    assert result


def test_lookup_session():

    manager = create_manager()

    session = create_session()

    manager.open(
        session
    )

    assert manager.lookup(
        "session-1"
    ) == session


def test_send():

    manager = create_manager()

    manager.open(
        create_session()
    )

    assert manager.send(
        "session-1",
        b"hello",
    )


def test_close():

    manager = create_manager()

    manager.open(
        create_session()
    )

    assert manager.close(
        "session-1"
    )


def test_snapshot():

    manager = create_manager()

    snapshot = manager.snapshot()

    assert "sessions" in snapshot
    assert "metrics" in snapshot