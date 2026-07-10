from influx.security.security_metrics import (
    SecurityMetrics,
)


def test_security_metrics():

    metrics = SecurityMetrics()

    metrics.record_byzantine_event()

    metrics.record_attack()

    metrics.record_blocked_action()

    metrics.record_allowed_action()

    metrics.record_policy_check()

    assert (
        metrics.byzantine_events
        == 1
    )

    assert (
        metrics.attacks_detected
        == 1
    )

    assert (
        metrics.blocked_actions
        == 1
    )

    assert (
        metrics.allowed_actions
        == 1
    )

    assert (
        metrics.policy_checks
        == 1
    )


def test_security_snapshot():

    metrics = SecurityMetrics()

    snapshot = metrics.snapshot()

    assert (
        "byzantine_events"
        in snapshot
    )

    assert (
        "attacks_detected"
        in snapshot
    )

    assert (
        "blocked_actions"
        in snapshot
    )