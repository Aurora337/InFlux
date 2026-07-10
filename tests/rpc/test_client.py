from influx.rpc.api import (
    RPCResponse,
)

from influx.rpc.client import (
    RPCClient,
)


def test_client_call():

    def transport(request):

        return RPCResponse(
            request_id=request.request_id,
            result="pong",
        )

    client = RPCClient(
        transport
    )

    response = client.call(
        method="ping",
        request_id="1",
    )

    assert (
        response.result
        == "pong"
    )


def test_client_parameters():

    def transport(request):

        return RPCResponse(
            request_id=request.request_id,
            result=request.params["value"],
        )

    client = RPCClient(
        transport
    )

    response = client.call(
        method="echo",
        params={
            "value": "hello",
        },
    )

    assert (
        response.result
        == "hello"
    )


def test_client_request_id():

    def transport(request):

        return RPCResponse(
            request_id=request.request_id,
        )

    client = RPCClient(
        transport
    )

    response = client.call(
        method="ping",
        request_id="abc",
    )

    assert (
        response.request_id
        == "abc"
    )