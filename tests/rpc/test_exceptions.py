from influx.rpc.exceptions import (
    RPCError,
    InvalidRequestError,
    MethodNotFoundError,
    InvalidResponseError,
    ConnectionError,
)


def test_rpc_exception_hierarchy():

    assert issubclass(
        InvalidRequestError,
        RPCError,
    )

    assert issubclass(
        MethodNotFoundError,
        RPCError,
    )

    assert issubclass(
        InvalidResponseError,
        RPCError,
    )

    assert issubclass(
        ConnectionError,
        RPCError,
    )