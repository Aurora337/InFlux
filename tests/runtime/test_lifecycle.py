from influx.runtime.lifecycle import RuntimeLifecycle
from influx.runtime.services import RuntimeServices


def test_initial_state() -> None:
    lifecycle = RuntimeLifecycle(RuntimeServices())

    assert lifecycle.started is False


def test_start_runtime() -> None:
    lifecycle = RuntimeLifecycle(RuntimeServices())

    lifecycle.start()

    assert lifecycle.started is True


def test_stop_runtime() -> None:
    lifecycle = RuntimeLifecycle(RuntimeServices())

    lifecycle.start()
    lifecycle.stop()

    assert lifecycle.started is False


def test_restart_runtime() -> None:
    lifecycle = RuntimeLifecycle(RuntimeServices())

    lifecycle.start()
    lifecycle.restart()

    assert lifecycle.started is True