from influx.network.transport.transport import Transport
from influx.network.transport.transport_session import TransportSession
from influx.network.transport.transport_type import TransportType


def test_transport_creation():
    transport = Transport(
        transport_id="ws-test",
        transport_type=TransportType.TCP,
    )

    assert transport.transport_id == "ws-test"
    assert transport.transport_type == TransportType.TCP


def test_session_open_close():
    transport = Transport(transport_id="ws-session")
    session = TransportSession(
        session_id="ws-sess-1",
        peer_id="ws-peer-1",
        transport_type=TransportType.TCP,
    )

    result = transport.open(session)
    assert result is True
    assert session.connected is True

    result = transport.close(session)
    assert result is True
    assert session.connected is False


def test_send_receive():
    transport = Transport(transport_id="ws-send")
    session = TransportSession(
        session_id="ws-sess-2",
        peer_id="ws-peer-2",
        transport_type=TransportType.TCP,
    )
    transport.open(session)

    data = b"websocket payload"
    result = transport.send(session, data)
    assert result is True

    result = transport.receive(session)
    assert result is True
