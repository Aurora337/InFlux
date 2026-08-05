from influx.runtime.dispatcher import RuntimeDispatcher
from influx.runtime.events import RuntimeEvent


def test_dispatch_event() -> None:
    dispatcher = RuntimeDispatcher()

    called = []

    def handler(event: RuntimeEvent) -> None:
        called.append(event)

    dispatcher.register(
        "TEST",
        handler,
    )

    event = RuntimeEvent(
        event_type="TEST",
        payload={},
    )

    count = dispatcher.dispatch(event)

    assert count == 1
    assert called[0] == event


def test_unknown_event() -> None:
    dispatcher = RuntimeDispatcher()

    event = RuntimeEvent(
        event_type="UNKNOWN",
        payload={},
    )

    assert dispatcher.dispatch(event) == 0