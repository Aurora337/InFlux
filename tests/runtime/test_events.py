from influx.runtime.events import (
    EventBus,
    RuntimeEvent,
)


def test_emit_event() -> None:
    bus = EventBus()

    event = RuntimeEvent(
        event_type="START",
        payload={"node": "A"},
    )

    bus.emit(event)

    assert bus.count() == 1
    assert bus.latest() == event


def test_empty_event_bus() -> None:
    bus = EventBus()

    assert bus.latest() is None
    assert bus.count() == 0