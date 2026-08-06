"""
Unit tests for the Event Bus.
"""

from influx.events.event import EventType
from influx.events.event_bus import EventBus


class TestEventBus:
    """Test EventBus class aligned to current API."""

    def test_publish_event(self):
        bus = EventBus()
        event = bus.publish_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={"msg": "hello"},
            block_height=0,
        )
        assert event is not None
        assert event.event_type == EventType.SYSTEM_STARTUP
        assert bus.queue.event_count() == 1

    def test_subscribe_global_and_publish(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        assert bus.subscribe(handler=handler) is True
        assert bus.get_subscriber_count() == 1

        bus.publish_event(EventType.SYSTEM_STARTUP, "system", {}, 0)
        assert len(received) == 1

    def test_subscribe_typed_and_publish(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        assert bus.subscribe(event_type=EventType.BLOCK_FINALIZED, handler=handler) is True
        bus.publish_event(EventType.SYSTEM_STARTUP, "system", {}, 0)
        bus.publish_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        assert len(received) == 1
        assert received[0].event_type == EventType.BLOCK_FINALIZED

    def test_unsubscribe_global(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe(handler=handler)
        assert bus.unsubscribe(handler) is True
        bus.publish_event(EventType.SYSTEM_STARTUP, "system", {}, 0)
        assert len(received) == 0

    def test_unsubscribe_typed(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe(event_type=EventType.BLOCK_FINALIZED, handler=handler)
        assert bus.unsubscribe(handler, EventType.BLOCK_FINALIZED) is True
        bus.publish_event(EventType.BLOCK_FINALIZED, "consensus", {}, 1)
        assert len(received) == 0

    def test_snapshot(self):
        bus = EventBus()
        bus.publish_event(EventType.SYSTEM_STARTUP, "system", {}, 0)
        snap = bus.snapshot()
        assert "queue" in snap
        assert "registry" in snap
        assert "total_subscribers" in snap
