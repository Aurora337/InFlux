from influx.network.transport.transport_config import TransportConfig


def test_default_config() -> None:
    config = TransportConfig(
        host="127.0.0.1",
        port=9000,
    )

    assert config.host == "127.0.0.1"
    assert config.port == 9000


def test_validate() -> None:
    config = TransportConfig(
        host="localhost",
        port=8080,
    )

    config.validate()