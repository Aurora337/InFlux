from influx.rpc.api import (
    RPCRequest,
    RPCResponse,
)


def test_rpc_request_creation():

    request = RPCRequest(
        method="get_state",
        params={
            "height": 10,
        },
        request_id="1",
    )

    assert (
        request.method
        == "get_state"
    )

    assert (
        request.request_id
        == "1"
    )


def test_rpc_request_serialization():

    request = RPCRequest(
        method="ping",
        request_id="1",
    )

    serialized = request.serialize()

    assert (
        '"method": "ping"'
        in serialized
    )


def test_rpc_response_success():

    response = RPCResponse(
        request_id="1",
        result={
            "status": "ok",
        },
    )

    assert (
        response.success()
        is True
    )


def test_rpc_response_error():

    response = RPCResponse(
        request_id="1",
        error="failure",
    )

    assert (
        response.success()
        is False
    )


def test_rpc_response_serialization():

    response = RPCResponse(
        request_id="1",
        result="ok",
    )

    serialized = response.serialize()

    assert (
        '"result": "ok"'
        in serialized
    )