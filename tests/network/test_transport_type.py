from influx.network.transport.transport_type import TransportType


def test_transport_types_exist() -> None:
    assert TransportType.TCP.name == "TCP"
    assert TransportType.QUIC.name == "QUIC"
    assert TransportType.MEMORY.name == "MEMORY"


def test_transport_values_unique() -> None:
    assert len(set(TransportType)) == len(TransportType)