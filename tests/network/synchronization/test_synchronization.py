from influx.network.synchronization.synchronization import (
    Synchronization,
)

from influx.network.synchronization.sync_message import (
    SyncMessage,
)

from influx.network.synchronization.sync_request import (
    SyncRequest,
)

from influx.network.synchronization.sync_response import (
    SyncResponse,
)

from influx.network.synchronization.sync_state import (
    SyncState,
)


def create_request():

    return SyncRequest(
        requester="node-a",
        target="node-b",
        range_start=0,
        range_end=10,
    )


def create_response():

    return SyncResponse(
        responder="node-b",
        requester="node-a",
        payload={
            "state": {},
        },
    )


def test_default_state():

    sync = Synchronization()

    assert (
        sync.state
        == SyncState.INITIALIZING
    )


def test_start():

    sync = Synchronization()

    sync.start()

    assert (
        sync.state
        == SyncState.IDLE
    )


def test_receive_request():

    sync = Synchronization()

    sync.start()

    result = sync.receive_request(
        create_request()
    )

    assert result
    assert (
        sync.state
        == SyncState.RECEIVING
    )


def test_receive_response():

    sync = Synchronization()

    sync.start()

    result = sync.receive_response(
        create_response()
    )

    assert result
    assert (
        sync.state
        == SyncState.VERIFYING
    )


def test_validate_message():

    sync = Synchronization()

    message = SyncMessage(
        source_node="node-a",
        target_node="node-b",
        payload={},
    )

    assert sync.validate_message(
        message
    )


def test_complete():

    sync = Synchronization()

    sync.complete()

    assert (
        sync.state
        == SyncState.COMPLETE
    )


def test_stop():

    sync = Synchronization()

    sync.stop()

    assert (
        sync.state
        == SyncState.STOPPED
    )


def test_snapshot():

    sync = Synchronization()

    snapshot = sync.snapshot()

    assert "state" in snapshot
    assert "metrics" in snapshot