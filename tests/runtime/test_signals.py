from influx.runtime.signals import RuntimeSignalHandler


def test_handler_invokes_shutdown() -> None:
    called = False

    def shutdown() -> None:
        nonlocal called
        called = True

    handler = RuntimeSignalHandler(shutdown)

    handler._handle(2, None)

    assert called