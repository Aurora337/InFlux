from influx.network.synchronization.sync_request import (
    SyncRequest,
)


def test_request_defaults():

    request = SyncRequest(
        requester="node-a",
        target="node-b",
    )

    assert request.requester == "node-a"
    assert request.target == "node-b"
    assert request.range_start == 0
    assert request.range_end == 0


def test_request_id_created():

    request = SyncRequest(
        requester="node-a",
        target="node-b",
    )

    assert request.request_id is not None


def test_request_snapshot():

    request = SyncRequest(
        requester="node-a",
        target="node-b",
        state_hash="hash1",
        range_start=10,
        range_end=20,
    )

    snapshot = request.snapshot()

    assert snapshot["requester"] == "node-a"
    assert snapshot["target"] == "node-b"
    assert snapshot["state_hash"] == "hash1"
    assert snapshot["range_start"] == 10
    assert snapshot["range_end"] == 20