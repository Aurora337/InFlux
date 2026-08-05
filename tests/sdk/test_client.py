from influx.sdk.client import InFluxClient
from influx.sdk.config import SDKConfig


def test_client_defaults() -> None:
    client = InFluxClient()

    assert client.connected is False
    assert client.endpoint == "http://127.0.0.1:8080"


def test_client_connect_disconnect() -> None:
    client = InFluxClient()

    client.connect()

    assert client.connected is True
    assert client.ping() is True

    client.disconnect()

    assert client.connected is False
    assert client.ping() is False


def test_custom_configuration() -> None:
    config = SDKConfig(
        host="localhost",
        port=9000,
        use_tls=True,
    )

    client = InFluxClient(config)

    assert client.endpoint == "https://localhost:9000"