from influx.interoperability.interop_metrics import (
    InteropMetrics,
)


def test_interop_metrics():

    metrics = InteropMetrics()

    metrics.record_bridge()
    metrics.record_sent()
    metrics.record_received()
    metrics.record_state_verified()
    metrics.record_verification_failure()

    assert metrics.bridges_created == 1
    assert metrics.messages_sent == 1
    assert metrics.messages_received == 1
    assert metrics.states_verified == 1
    assert metrics.verification_failures == 1


def test_snapshot():

    metrics = InteropMetrics()

    snapshot = metrics.snapshot()

    assert "bridges_created" in snapshot
    assert "messages_sent" in snapshot
    assert "messages_received" in snapshot
    assert "states_verified" in snapshot
    assert "verification_failures" in snapshot