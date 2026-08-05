from influx.network.transport.transport import Transport
from influx.network.transport.transport_config import TransportConfig
from influx.network.transport.transport_session import TransportSession
from influx.network.transport.transport_type import TransportType


def create_transport() -> Transport:
    return Transport(
        transport_id="transport-1",
        transport_type=TransportType.TCP,
        config=TransportConfig(
            host="127.0.0.1",
            port=9000,
        ),
    ) 


def create_session() -> TransportSession:
    return TransportSession(
        session_id="session-1",
        peer_id="peer-1",
        transport_type=TransportType.TCP,
    )


def test_transport_open() -> None:
    transport = create_transport()
    session = create_session()

    assert not transport.active

    assert transport.open(session)

    assert transport.active


def test_transport_close() -> None:
    transport = create_transport()
    session = create_session()

    transport.open(session)

    assert transport.close(session)

    assert not transport.active


def test_transport_heartbeat() -> None:
    transport = create_transport()
    session = create_session()

    assert not transport.heartbeat(session)

    transport.open(session)

    assert transport.heartbeat(session)


def test_transport_send() -> None:
    transport = create_transport()
    session = create_session()

    assert not transport.send(
        session,
        b"hello",
    )

    transport.open(session)

    assert transport.send(
        session,
        b"hello",
    )


def test_transport_receive() -> None:
    transport = create_transport()
    session = create_session()

    transport.open(session)

    assert not transport.receive(session)

    transport.send(
        session,
        b"hello",
    )

    assert transport.receive(session)

