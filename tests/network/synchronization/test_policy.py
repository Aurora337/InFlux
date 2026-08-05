from influx.network.synchronization.sync_policy import (
    SyncPolicy,
)


def test_policy_defaults():

    policy = SyncPolicy()

    assert policy.max_range_size == 10000
    assert not policy.require_signature


def test_valid_request():

    policy = SyncPolicy()

    result = policy.validate_request(
        requester="node-a",
        target="node-b",
        range_start=0,
        range_end=100,
    )

    assert result


def test_reject_missing_requester():

    policy = SyncPolicy()

    result = policy.validate_request(
        requester="",
        target="node-b",
        range_start=0,
        range_end=100,
    )

    assert not result


def test_reject_invalid_range():

    policy = SyncPolicy()

    result = policy.validate_request(
        requester="node-a",
        target="node-b",
        range_start=100,
        range_end=10,
    )

    assert not result


def test_reject_large_range():

    policy = SyncPolicy(
        max_range_size=10,
    )

    result = policy.validate_request(
        requester="node-a",
        target="node-b",
        range_start=0,
        range_end=20,
    )

    assert not result


def test_signature_required():

    policy = SyncPolicy(
        require_signature=True,
    )

    result = policy.validate_response(
        payload_size=10,
        signature="",
    )

    assert not result


def test_snapshot():

    policy = SyncPolicy()

    snapshot = policy.snapshot()

    assert "max_payload_size" in snapshot
    assert "max_range_size" in snapshot