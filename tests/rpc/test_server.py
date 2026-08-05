import pytest

from influx.rpc.api import (
    RPCRequest,
)

from influx.rpc.server import (
    RPCServer,
)

from influx.rpc.exceptions import (
    MethodNotFoundError,
)


def test_server_register_method():

    server = RPCServer()

    server.register_method(
        "ping",
        lambda: "pong",
    )

    request = RPCRequest(
        method="ping",
    )

    response = server.handle(
        request
    )

    assert (
        response.result
        == "pong"
    )


def test_server_with_parameters():

    server = RPCServer()

    server.register_method(
        "add",
        lambda a, b: a + b,
    )

    request = RPCRequest(
        method="add",
        params={
            "a": 2,
            "b": 3,
        },
    )

    response = server.handle(
        request
    )

    assert (
        response.result
        == 5
    )


def test_missing_method():

    server = RPCServer()

    request = RPCRequest(
        method="unknown",
    )

    with pytest.raises(
        MethodNotFoundError
    ):

        server.handle(
            request
        )