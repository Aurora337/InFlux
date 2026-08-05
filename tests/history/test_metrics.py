from influx.history.history_metrics import (
    HistoryMetrics,
)


def test_history_metrics():

    metrics = HistoryMetrics()

    metrics.record_state()

    metrics.record_replay(
        True
    )

    metrics.record_replay(
        False
    )

    metrics.record_query()

    metrics.record_verification(
        True
    )

    metrics.record_verification(
        False
    )

    assert (
        metrics.states_recorded
        == 1
    )

    assert (
        metrics.successful_replays
        == 1
    )

    assert (
        metrics.failed_replays
        == 1
    )

    assert (
        metrics.queries
        == 1
    )

    assert (
        metrics.successful_verifications
        == 1
    )

    assert (
        metrics.failed_verifications
        == 1
    )


def test_metrics_snapshot():

    metrics = HistoryMetrics()

    snapshot = metrics.snapshot()

    assert (
        "states_recorded"
        in snapshot
    )

    assert (
        "replay_attempts"
        in snapshot
    )

    assert (
        "root_verifications"
        in snapshot
    )