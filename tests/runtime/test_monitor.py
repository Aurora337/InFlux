from influx.runtime.monitor import RuntimeMonitor


def test_monitor_start_stop() -> None:
    monitor = RuntimeMonitor()

    monitor.start()
    assert monitor.running

    monitor.stop()
    assert not monitor.running


def test_monitor_record_execution() -> None:
    monitor = RuntimeMonitor()

    monitor.record(object())

    assert monitor.metrics.executed == 1


def test_monitor_record_dispatch() -> None:
    monitor = RuntimeMonitor()

    monitor.record_dispatch()

    assert monitor.metrics.dispatched == 1


def test_monitor_record_failure() -> None:
    monitor = RuntimeMonitor()

    monitor.record_failure()

    assert monitor.metrics.failed == 1


def test_monitor_reset() -> None:
    monitor = RuntimeMonitor()

    monitor.record_dispatch()
    monitor.record(object())
    monitor.record_failure()

    monitor.reset()

    assert monitor.metrics.dispatched == 0
    assert monitor.metrics.executed == 0
    assert monitor.metrics.failed == 0