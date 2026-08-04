from influx.network.transport.transport import Transport
from influx.network.transport.transport_type import TransportType


def test_transport_creation():
    transport = Transport(
        transport_id="test",
        transport_type=TransportType.MEMORY,
    )

    assert transport.transport_id == "test"
    assert transport.transport_type == TransportType.MEMORY
    assert transport.config is not None


def test_transport_active_property():
    transport = Transport()
    assert transport.active is False
