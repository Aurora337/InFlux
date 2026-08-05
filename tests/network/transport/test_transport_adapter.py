from influx.network.transport.transport_adapter import (
    TransportAdapter,
)
from influx.network.transport.transport_session import (
    TransportSession,
)
from influx.network.transport.transport_type import (
    TransportType,
)


class MockTransport:

    def open(
        self,
        session,
    ):
        return True

    def close(
        self,
        session,
    ):
        return True

    def send(
        self,
        session,
        data,
    ):
        return True

    def receive(
        self,
        session,
    ):
        return True

    def heartbeat(
        self,
        session,
    ):
        return True


def create_session():

    return TransportSession(
        session_id="session-1",
        peer_id="node-1",
        transport_type=TransportType.TCP,
    )


def test_adapter_open():

    adapter = TransportAdapter(
        MockTransport()
    )

    assert adapter.open(
        create_session()
    )


def test_adapter_close():

    adapter = TransportAdapter(
        MockTransport()
    )

    assert adapter.close(
        create_session()
    )


def test_adapter_send():

    adapter = TransportAdapter(
        MockTransport()
    )

    assert adapter.send(
        create_session(),
        b"hello",
    )


def test_adapter_receive():

    adapter = TransportAdapter(
        MockTransport()
    )

    assert adapter.receive(
        create_session()
    )


def test_adapter_heartbeat():

    adapter = TransportAdapter(
        MockTransport()
    )

    assert adapter.heartbeat(
        create_session()
    )