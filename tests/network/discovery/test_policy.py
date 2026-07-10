from influx.network.discovery.discovery_policy import (
    DiscoveryPolicy,
)


def test_policy_defaults():

    policy = DiscoveryPolicy()

    assert policy.max_peers == 64
    assert policy.require_active


def test_accept_active_peer():

    policy = DiscoveryPolicy()

    result = policy.validate_peer(
        trust_score=1.0,
        active=True,
    )

    assert result


def test_reject_inactive_peer():

    policy = DiscoveryPolicy()

    result = policy.validate_peer(
        trust_score=1.0,
        active=False,
    )

    assert not result


def test_reject_low_trust():

    policy = DiscoveryPolicy(
        minimum_trust_score=0.5,
    )

    result = policy.validate_peer(
        trust_score=0.1,
        active=True,
    )

    assert not result


def test_snapshot():

    policy = DiscoveryPolicy()

    snapshot = policy.snapshot()

    assert "max_peers" in snapshot
    assert "prevent_duplicates" in snapshot