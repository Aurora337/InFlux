"""
Unit tests for the Event Dispatcher.
"""

import pytest
from influx.events.event import Event, EventType, create_event
from influx.events.event_dispatcher import EventDispatcher, DispatchReceipt
from influx.events.event_registry import EventRegistry


class TestEventDispatcher:
    """Test EventDispatcher class."""

    def test_register_handler(self):
        """Test registering an event handler."""
        dispatcher = EventDispatcher()

        def handler(event):
            return {"status": "processed"}

        result = dispatcher.register(
            event_type=EventType.BLOCK_FINALIZED,
            handler=handler,
        )
        assert result is True
        assert dispatcher.handler_count() == 1

    def test_register_duplicate_handler(self):
        """Test that duplicate registration fails."""
        dispatcher = EventDispatcher()

        def handler(event):
            return {"status": "processed"}

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        result = dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        assert result is False

    def test_unregister_handler(self):
        """Test unregistering a handler."""
        dispatcher = EventDispatcher()

        def handler(event):
            return {"status": "processed"}

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        result = dispatcher.unregister(EventType.BLOCK_FINALIZED)
        assert result is True
        assert dispatcher.handler_count() == 0

    def test_unregister_nonexistent(self):
        """Test unregistering a non-existent handler."""
        dispatcher = EventDispatcher()
        result = dispatcher.unregister(EventType.BLOCK_FINALIZED)
        assert result is False

    def test_dispatch_event(self):
        """Test dispatching an event to a handler."""
        dispatcher = EventDispatcher()
        results = []

        def handler(event):
            results.append(event.event_type)
            return {"status": "processed"}

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        event = create_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        receipt = dispatcher.dispatch(event)

        assert receipt.success is True
        assert len(results) == 1
        assert results[0] == EventType.BLOCK_FINALIZED

    def test_dispatch_no_handler(self):
        """Test dispatching an event with no registered handler."""
        dispatcher = EventDispatcher()
        event = create_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        receipt = dispatcher.dispatch(event)

        assert receipt.success is False
        assert "No handler" in receipt.error

    def test_dispatch_handler_error(self):
        """Test dispatching when handler raises an error."""
        dispatcher = EventDispatcher()

        def failing_handler(event):
            raise ValueError("Handler error")

        dispatcher.register(EventType.BLOCK_FINALIZED, failing_handler)
        event = create_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        receipt = dispatcher.dispatch(event)

        assert receipt.success is False
        assert receipt.error is not None

    def test_dispatch_multiple_handlers(self):
        """Test dispatching to multiple handlers."""
        dispatcher = EventDispatcher()
        results = []

        def handler1(event):
            results.append("handler1")

        def handler2(event):
            results.append("handler2")

        dispatcher.register(EventType.BLOCK_FINALIZED, handler1)
        dispatcher.register(EventType.BLOCK_FINALIZED, handler2)
        event = create_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        receipt = dispatcher.dispatch(event)

        assert receipt.success is True
        assert len(results) == 2

    def test_dispatch_handler_error_isolation(self):
        """Test that one failing handler doesn't affect others."""
        dispatcher = EventDispatcher()
        results = []

        def failing_handler(event):
            raise ValueError("Failed")

        def good_handler(event):
            results.append("success")

        dispatcher.register(EventType.BLOCK_FINALIZED, failing_handler)
        dispatcher.register(EventType.BLOCK_FINALIZED, good_handler)
        event = create_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        receipt = dispatcher.dispatch(event)

        # Should be successful because at least one handler succeeded
        assert receipt.success is True
        assert len(results) == 1

    def test_dispatch_with_registry_validation(self):
        """Test dispatching with registry validation."""
        dispatcher = EventDispatcher()
        registry = EventRegistry()
        registry.register(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            required_fields=["block"],
        )

        def handler(event):
            return {"status": "ok"}

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)

        valid_event = create_event(
            EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1
        )
        receipt = dispatcher.dispatch(valid_event, registry)
        assert receipt.success is True

        invalid_event = create_event(
            EventType.BLOCK_FINALIZED, "consensus", {"other": "data"}, 1
        )
        receipt = dispatcher.dispatch(invalid_event, registry)
        assert receipt.success is False

    def test_has_handler(self):
        """Test checking for registered handlers."""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        assert dispatcher.has_handler(EventType.BLOCK_FINALIZED) is False
        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        assert dispatcher.has_handler(EventType.BLOCK_FINALIZED) is True

    def test_get_handler(self):
        """Test getting a registered handler."""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        retrieved = dispatcher.get_handler(EventType.BLOCK_FINALIZED)
        assert retrieved == handler

    def test_get_handler_not_found(self):
        """Test getting a non-existent handler."""
        dispatcher = EventDispatcher()
        retrieved = dispatcher.get_handler(EventType.BLOCK_FINALIZED)
        assert retrieved is None

    def test_get_registered_types(self):
        """Test getting all registered event types."""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        dispatcher.register(EventType.SYSTEM_STARTUP, handler)
        types = dispatcher.get_registered_types()
        assert len(types) == 2

    def test_clear(self):
        """Test clearing all handlers."""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        assert dispatcher.handler_count() == 1
        dispatcher.clear()
        assert dispatcher.handler_count() == 0

    def test_snapshot(self):
        """Test dispatcher snapshot."""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.register(EventType.BLOCK_FINALIZED, handler)
        snap = dispatcher.snapshot()
        assert snap["handler_count"] == 1
        assert "block_finalized" in snap["registered_types"]


class TestDispatchReceipt:
    """Test DispatchReceipt class."""

    def test_successful_receipt(self):
        """Test creating a successful receipt."""
        event = create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)
        receipt = DispatchReceipt(
            event_id=event.event_id,
            event_type=EventType.SYSTEM_STARTUP,
            success=True,
            results=[{"status": "ok"}],
        )
        assert receipt.success is True
        assert receipt.event_type == EventType.SYSTEM_STARTUP
        assert len(receipt.results) == 1

    def test_failed_receipt(self):
        """Test creating a failed receipt."""
        receipt = DispatchReceipt(
            event_id="evt_001",
            event_type=EventType.BLOCK_FINALIZED,
            success=False,
            error="Handler not found",
        )
        assert receipt.success is False
        assert receipt.error == "Handler not found"

    def test_snapshot(self):
        """Test receipt snapshot."""
        receipt = DispatchReceipt(
            event_id="evt_001",
            event_type=EventType.SYSTEM_STARTUP,
            success=True,
        )
        snap = receipt.snapshot()
        assert snap["event_id"] == "evt_001"
        assert snap["event_type"] == "system_startup"
        assert snap["success"] is True
