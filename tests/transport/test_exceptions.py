from influx.transport.exceptions import (
    TransportError,
    ConnectionError,
    ProtocolError,
    MessageValidationError,
)


def test_exception_hierarchy():

    assert issubclass(
        ConnectionError,
        TransportError,
    )

    assert issubclass(
        ProtocolError,
        TransportError,
    )

    assert issubclass(
        MessageValidationError,
        ProtocolError,
    )