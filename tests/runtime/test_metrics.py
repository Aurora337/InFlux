from influx.runtime.metrics import RuntimeMetrics


def test_metrics_initial_state() -> None:
    metrics = RuntimeMetrics()

    assert metrics.dispatched == 0
    assert metrics.executed == 0
    assert metrics.failed == 0


def test_record_dispatch() -> None:
    metrics = RuntimeMetrics()

    metrics.record_dispatch()

    assert metrics.dispatched == 1


def test_record_execution() -> None:
    metrics = RuntimeMetrics()

    metrics.record_execution()

    assert metrics.executed == 1


def test_record_failure() -> None:
    metrics = RuntimeMetrics()

    metrics.record_failure()

    assert metrics.failed == 1


def test_reset() -> None:
    metrics = RuntimeMetrics()

    metrics.record_dispatch()
    metrics.record_execution()
    metrics.record_failure()

    metrics.reset()

    assert metrics.dispatched == 0
    assert metrics.executed == 0
    assert metrics.failed == 0