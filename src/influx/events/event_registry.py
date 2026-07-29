"""
Deterministic event type registry for the InFlux protocol.

Provides event type registration, validation, and lookup
to ensure all emitted events are known and properly structured.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .event import Event, EventType


@dataclass(slots=True)
class EventRegistration:
    """
    Registration record for an event type.

    Stores metadata about the event type including
    the expected payload schema and validation rules.
    """

    event_type: EventType
    source: str
    description: str
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute deterministic registration hash."""
        canonical = {
            "event_type": self.event_type.value,
            "source": self.source,
            "description": self.description,
            "required_fields": sorted(self.required_fields),
            "optional_fields": sorted(self.optional_fields),
            "version": self.version,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def snapshot(self) -> dict[str, Any]:
        """Deterministic registration snapshot."""
        return {
            "event_type": self.event_type.value,
            "source": self.source,
            "description": self.description,
            "required_fields": sorted(self.required_fields),
            "optional_fields": sorted(self.optional_fields),
            "version": self.version,
            "hash": self.hash,
        }


@dataclass(slots=True)
class EventRegistry:
    """
    Deterministic event type registry.

    Manages:
    - Event type registration
    - Payload schema validation
    - Event source verification
    - Registration lookup and enumeration
    """

    _registrations: dict[str, EventRegistration] = field(default_factory=dict)
    _validators: dict[str, list[Callable[[Event], bool]]] = field(default_factory=dict)

    def register(
        self,
        event_type: EventType,
        source: str,
        description: str = "",
        required_fields: Optional[list[str]] = None,
        optional_fields: Optional[list[str]] = None,
        version: str = "1.0.0",
    ) -> bool:
        """
        Register an event type with the registry.

        Args:
            event_type: The event type to register
            source: The subsystem that emits this event type
            description: Human-readable description
            required_fields: Fields that must be present in the payload
            optional_fields: Fields that may be present in the payload
            version: Schema version string

        Returns:
            True if registration was successful
        """
        type_key = event_type.value

        if type_key in self._registrations:
            return False

        registration = EventRegistration(
            event_type=event_type,
            source=source,
            description=description,
            required_fields=required_fields or [],
            optional_fields=optional_fields or [],
            version=version,
        )

        self._registrations[type_key] = registration
        return True

    def is_registered(self, event_type: EventType) -> bool:
        """Check if an event type is registered."""
        return event_type.value in self._registrations

    def get_registration(self, event_type: EventType) -> Optional[EventRegistration]:
        """Get the registration for an event type."""
        return self._registrations.get(event_type.value)

    def validate_event(self, event: Event) -> bool:
        registration = self.get_registration(event.event_type)

        if registration is None:
            return False

        if registration.source != event.source:
            return False

        for field_name in registration.required_fields:
            if field_name not in event.payload:
                return False

        type_key = event.event_type.value

        for validator in self._validators.get(type_key, []):
            if not validator(event):
                return False

        return True

    def validate(self, event: Event) -> bool:
        """
        Compatibility wrapper for event validation.

        Performs:
        - registration lookup
        - source validation
        - payload validation
        - custom validator execution
        """

        registration = self.get_registration(event.event_type)

        if registration is None:
            return False

        # Verify source
        if registration.source != event.source:
            return False

        return self.validate_event(event)

    def add_validator(
        self,
        event_type: EventType,
        validator: Callable[[Event], bool],
    ) -> bool:
        """
        Add a custom validator function for an event type.

        Args:
            event_type: The event type to validate
            validator: Function that takes an Event and returns bool

        Returns:
            True if the validator was added
        """
        type_key = event_type.value
        if type_key not in self._registrations:
            return False

        if type_key not in self._validators:
            self._validators[type_key] = []

        self._validators[type_key].append(validator)
        return True

    def get_registered_types(self) -> list[EventType]:
        """Get all registered event types."""
        return [reg.event_type for reg in self._registrations.values()]

    def get_registrations_by_source(self, source: str) -> list[EventRegistration]:
        """Get all registrations from a specific source subsystem."""
        return [
            reg for reg in self._registrations.values() if reg.source == source
        ]

    def registration_count(self) -> int:
        """Get the number of registered event types."""
        return len(self._registrations)

    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic registry snapshot.
        """

        return {
            "registration_count": self.registration_count(),

            "registered_types": [
                event_type.value
                for event_type in self.get_registered_types()
            ],

            "registrations": {
                key: registration.snapshot()
                for key, registration in sorted(
                    self._registrations.items()
                )
            },

            "validator_count": sum(
                len(validators)
                for validators in self._validators.values()
            ),
        }

    def reset(self) -> None:
        """Reset the registry to empty state."""
        self._registrations.clear()
        self._validators.clear()
