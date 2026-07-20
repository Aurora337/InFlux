from influx.network.transport.transport_adapter import TransportAdapter
from influx.network.transport.transport_session import TransportSession
from influx.network.transport.transport_type import TransportType
from tests.network.transport.test_transport import MockTransport


def create_session():

    return TransportSession(
        session_id="session-1",
        peer_id="node-a",
        transport_type=TransportType.LOCAL,
    )


def test_open():

    adapter = TransportAdapter(
        MockTransport()
    )

    session = create_session()

    assert adapter.open(session)

    assert session.connected


def test_close():

    adapter = TransportAdapter(
        MockTransport()
    )

    session = create_session()

    adapter.open(session)

    assert adapter.close(session)

    assert not session.connected


def test_send():

    adapter = TransportAdapter(
        MockTransport()
    )

    session = create_session()

    adapter.open(session)

    assert adapter.send(
        session,
        b"hello",
    )

    assert session.bytes_sent == 5


def test_receive():

    adapter = TransportAdapter(
        MockTransport()
    )

    session = create_session()

    adapter.open(session)

    assert adapter.receive(
        session,
    )

    assert session.connected


def test_heartbeat():

    adapter = TransportAdapter(
        MockTransport()
    )

    session = create_session()

    adapter.open(session)

    assert adapter.heartbeat(session)