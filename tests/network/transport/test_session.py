from influx.network.transport.transport_session import TransportSession
from influx.network.transport.transport_type import TransportType


def create_session():

    return TransportSession(
        session_id="session-1",
        peer_id="node-a",
        transport_type=TransportType.LOCAL,
    )


def test_session_defaults():

    session = create_session()

    assert not session.connected
    assert session.bytes_sent == 0
    assert session.bytes_received == 0


def test_open():

    session = create_session()

    session.open()

    assert session.connected


def test_close():

    session = create_session()

    session.open()

    session.close()

    assert not session.connected


def test_touch():

    session = create_session()

    original = session.last_activity

    session.touch()

    assert session.last_activity >= original


def test_record_send():

    session = create_session()

    session.record_send(100)

    assert session.bytes_sent == 100


def test_record_receive():

    session = create_session()

    session.record_receive(200)

    assert session.bytes_received == 200


def test_snapshot():

    session = create_session()

    snapshot = session.snapshot()

    assert snapshot["session_id"] == "session-1"
    assert snapshot["peer_id"] == "node-a"