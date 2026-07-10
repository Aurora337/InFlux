from influx.network.synchronization.sync_response import (
    SyncResponse,
)


def test_response_defaults():

    response = SyncResponse(
        responder="node-b",
        requester="node-a",
        payload={
            "state": {},
        },
    )

    assert response.responder == "node-b"
    assert response.requester == "node-a"
    assert response.accepted


def test_response_id_created():

    response = SyncResponse(
        responder="node-b",
        requester="node-a",
        payload={},
    )

    assert response.response_id is not None


def test_response_snapshot():

    response = SyncResponse(
        responder="node-b",
        requester="node-a",
        payload={
            "block": 100,
        },
        state_hash="xyz789",
        accepted=True,
    )

    snapshot = response.snapshot()

    assert snapshot["responder"] == "node-b"
    assert snapshot["requester"] == "node-a"
    assert snapshot["state_hash"] == "xyz789"
    assert snapshot["accepted"]