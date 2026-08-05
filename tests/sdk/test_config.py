import pytest

from influx.sdk.config import SDKConfig
from influx.sdk.exceptions import ConfigurationError


def test_default_configuration() -> None:
    config = SDKConfig()

    assert config.host == "127.0.0.1"
    assert config.port == 8080
    assert config.timeout == 30.0
    assert config.use_tls is False


def test_base_url_http() -> None:
    config = SDKConfig()

    assert config.base_url == "http://127.0.0.1:8080"


def test_base_url_https() -> None:
    config = SDKConfig(use_tls=True)

    assert config.base_url == "https://127.0.0.1:8080"


def test_validate_success() -> None:
    SDKConfig().validate()


def test_invalid_host() -> None:
    with pytest.raises(ConfigurationError):
        SDKConfig(host="").validate()


def test_invalid_port() -> None:
    with pytest.raises(ConfigurationError):
        SDKConfig(port=0).validate()


def test_invalid_timeout() -> None:
    with pytest.raises(ConfigurationError):
        SDKConfig(timeout=0).validate()