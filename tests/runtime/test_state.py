from influx.runtime.state import RuntimeState


def test_initial_state() -> None:
    state = RuntimeState()

    assert state.started is False
    assert state.stopping is False
    assert state.healthy is True


def test_start() -> None:
    state = RuntimeState()

    state.start()

    assert state.started is True
    assert state.stopping is False


def test_stop() -> None:
    state = RuntimeState()

    state.start()
    state.stop()

    assert state.started is False
    assert state.stopping is True


def test_health_changes() -> None:
    state = RuntimeState()

    state.mark_unhealthy()
    assert state.healthy is False

    state.mark_healthy()
    assert state.healthy is True