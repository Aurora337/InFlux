"""
Unit tests for the Event Registry.
"""

from influx.events.event import EventType, create_event
from influx.events.event_registry import EventRegistry, EventRegistration


class TestEventRegistry:
    """Test EventRegistry class."""

    def test_register_event_type(self):
        """Test registering a new event type."""
        registry = EventRegistry()
        result = registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            description="System startup event",
        )
        assert result is True
        assert registry.is_registered(EventType.SYSTEM_STARTUP) is True

    def test_register_duplicate(self):
        """Test that duplicate registration fails."""
        registry = EventRegistry()
        registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
        )
        result = registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
        )
        assert result is False

    def test_is_registered(self):
        """Test checking if event type is registered."""
        registry = EventRegistry()
        assert registry.is_registered(EventType.SYSTEM_STARTUP) is False
        registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
        )
        assert registry.is_registered(EventType.SYSTEM_STARTUP) is True

    def test_get_registration(self):
        """Test retrieving a registration."""
        registry = EventRegistry()
        registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            description="Test event",
            required_fields=["message"],
            optional_fields=["version"],
            version="1.0.0",
        )
        reg = registry.get_registration(EventType.SYSTEM_STARTUP)
        assert reg is not None
        assert reg.event_type == EventType.SYSTEM_STARTUP
        assert reg.source == "system"
        assert reg.description == "Test event"
        assert "message" in reg.required_fields
        assert "version" in reg.optional_fields
        assert reg.version == "1.0.0"

    def test_get_registration_not_found(self):
        """Test retrieving a non-existent registration."""
        registry = EventRegistry()
        reg = registry.get_registration(EventType.SYSTEM_STARTUP)
        assert reg is None

    def test_validate_event_valid(self):
        """Test validating a valid event."""
        registry = EventRegistry()
        registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            required_fields=["message"],
        )
        event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={"message": "hello"},
            block_height=0,
        )
        assert registry.validate_event(event) is True

    def test_validate_event_missing_required(self):
        """Test that missing required fields fails validation."""
        registry = EventRegistry()
        registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            required_fields=["message"],
        )
        event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={"other": "data"},
            block_height=0,
        )
        assert registry.validate_event(event) is False

    def test_validate_event_unregistered(self):
        """Test that unregistered event types fail validation."""
        registry = EventRegistry()
        event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        assert registry.validate_event(event) is False

    def test_add_validator(self):
        """Test adding a custom validator."""
        registry = EventRegistry()
        registry.register(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
        )

        def custom_validator(event):
            return "valid" in event.payload

        result = registry.add_validator(EventType.SYSTEM_STARTUP, custom_validator)
        assert result is True

        valid_event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={"valid": True},
            block_height=0,
        )
        invalid_event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={"other": True},
            block_height=0,
        )
        assert registry.validate_event(valid_event) is True
        assert registry.validate_event(invalid_event) is False

    def test_get_registered_types(self):
        """Test getting all registered event types."""
        registry = EventRegistry()
        registry.register(EventType.SYSTEM_STARTUP, "system")
        registry.register(EventType.BLOCK_FINALIZED, "consensus")
        registry.register(EventType.BALANCE_CHANGED, "economics")
        types = registry.get_registered_types()
        assert len(types) == 3
        assert EventType.SYSTEM_STARTUP in types
        assert EventType.BLOCK_FINALIZED in types
        assert EventType.BALANCE_CHANGED in types

    def test_get_registrations_by_source(self):
        """Test getting registrations by source."""
        registry = EventRegistry()
        registry.register(EventType.SYSTEM_STARTUP, "system")
        registry.register(EventType.SYSTEM_SHUTDOWN, "system")
        registry.register(EventType.BLOCK_FINALIZED, "consensus")
        system_regs = registry.get_registrations_by_source("system")
        assert len(system_regs) == 2
        consensus_regs = registry.get_registrations_by_source("consensus")
        assert len(consensus_regs) == 1

    def test_registration_count(self):
        """Test registration count."""
        registry = EventRegistry()
        assert registry.registration_count() == 0
        registry.register(EventType.SYSTEM_STARTUP, "system")
        assert registry.registration_count() == 1
        registry.register(EventType.BLOCK_FINALIZED, "consensus")
        assert registry.registration_count() == 2

    def test_snapshot(self):
        """Test registry snapshot."""
        registry = EventRegistry()
        registry.register(EventType.SYSTEM_STARTUP, "system", description="Startup")
        snap = registry.snapshot()
        assert snap["registration_count"] == 1
        assert "system_startup" in snap["registrations"]

    def test_reset(self):
        """Test resetting the registry."""
        registry = EventRegistry()
        registry.register(EventType.SYSTEM_STARTUP, "system")
        assert registry.registration_count() == 1
        registry.reset()
        assert registry.registration_count() == 0


class TestEventRegistration:
    """Test EventRegistration class."""

    def test_compute_hash(self):
        """Test registration hash computation."""
        reg = EventRegistration(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            description="Test",
            required_fields=["msg"],
        )
        h = reg.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    def test_hash_determinism(self):
        """Test that same registration produces same hash."""
        reg1 = EventRegistration(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            description="Test",
        )
        reg2 = EventRegistration(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            description="Test",
        )
        assert reg1.hash == reg2.hash

    def test_snapshot(self):
        """Test registration snapshot."""
        reg = EventRegistration(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            description="Startup event",
            required_fields=["msg"],
        )
        snap = reg.snapshot()
        assert snap["event_type"] == "system_startup"
        assert snap["source"] == "system"
        assert snap["description"] == "Startup event"
        assert "msg" in snap["required_fields"]
