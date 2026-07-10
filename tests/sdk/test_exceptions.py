from influx.sdk.exceptions import (
    ConfigurationError,
    ConnectionFailedError,
    RPCRequestError,
    SDKError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(ConfigurationError, SDKError)
    assert issubclass(ConnectionFailedError, SDKError)
    assert issubclass(RPCRequestError, SDKError)


def test_exception_messages() -> None:
    error = ConfigurationError("invalid configuration")
    assert str(error) == "invalid configuration"

    error = ConnectionFailedError("connection failed")
    assert str(error) == "connection failed"

    error = RPCRequestError("rpc failed")
    assert str(error) == "rpc failed"