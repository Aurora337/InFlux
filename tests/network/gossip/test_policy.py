from influx.network.gossip.gossip_policy import (
    GossipPolicy,
)


def test_policy_defaults():

    policy = GossipPolicy()

    assert policy.max_ttl == 8
    assert policy.prevent_duplicates


def test_valid_message():

    policy = GossipPolicy()

    result = policy.validate_message(
        ttl=5,
        hops=1,
        signature="",
    )

    assert result


def test_reject_large_ttl():

    policy = GossipPolicy(
        max_ttl=4,
    )

    result = policy.validate_message(
        ttl=8,
        hops=1,
        signature="",
    )

    assert not result


def test_reject_too_many_hops():

    policy = GossipPolicy(
        max_hops=3,
    )

    result = policy.validate_message(
        ttl=2,
        hops=5,
        signature="",
    )

    assert not result


def test_signature_required():

    policy = GossipPolicy(
        require_signature=True,
    )

    result = policy.validate_message(
        ttl=2,
        hops=0,
        signature="",
    )

    assert not result


def test_snapshot():

    policy = GossipPolicy()

    snapshot = policy.snapshot()

    assert "max_ttl" in snapshot
    assert "max_hops" in snapshot