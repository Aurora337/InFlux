"""
Deterministic publish/subscribe event bus for the InFlux protocol.

Provides ordered event delivery, subscriber management,
and deterministic event routing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .event import Event, EventType
from .event_queue import EventQueue
from .event_registry import EventRegistry
from .event_filter import EventFilter


EventHandler = Callable[[Event], None]


@dataclass(slots=True)
class EventBus:
    """
    Deterministic publish/subscribe event bus.

    Manages:
    - Event publishing to the queue
    - Subscriber registration and notification
    - Event filtering per subscriber
    - Ordered event delivery
    """

    queue: EventQueue = field(default_factory=EventQueue)
    registry: EventRegistry = field(default_factory=EventRegistry)
    _subscribers: dict[str, list[tuple[Optional[EventFilter], EventHandler]]] = field(
        default_factory=dict
    )
    _global_subscribers: list[EventHandler] = field(default_factory=list)

    def subscribe(
        self,
        event_type: Optional[EventType] = None,
        handler: Optional[EventHandler] = None,
        event_filter: Optional[EventFilter] = None,
    ) -> bool:
        """
        Subscribe a handler to events.

        Args:
            event_type: Optional specific event type to subscribe to
            handler: The handler function to invoke on matching events
            event_filter: Optional filter for fine-grained event matching

        Returns:
            True if subscription was successful
        """
        if handler is None:
            return False

        if event_type is None and event_filter is None:
            # Subscribe to all events
            if handler not in self._global_subscribers:
                self._global_subscribers.append(handler)
            return True

        if event_type is not None:
            type_key = event_type.value
            if type_key not in self._subscribers:
                self._subscribers[type_key] = []
            self._subscribers[type_key].append((event_filter, handler))
            return True

        return False

    def unsubscribe(
        self,
        handler: EventHandler,
        event_type: Optional[EventType] = None,
    ) -> bool:
        """
        Unsubscribe a handler from events.

        Args:
            handler: The handler to remove
            event_type: Optional specific event type to unsubscribe from

        Returns:
            True if handler was found and removed
        """
        if handler in self._global_subscribers:
            self._global_subscribers.remove(handler)
            return True

        if event_type is not None:
            type_key = event_type.value
            if type_key in self._subscribers:
                self._subscribers[type_key] = [
                    (f, h) for f, h in self._subscribers[type_key] if h != handler
                ]
                return True

        return False

    def publish(
        self,
        event: Event,
    ) -> None:
        """
        Publish an event to the bus.

        The event is:
        1. Validated against the registry
        2. Pushed to the event queue
        3. Dispatched to matching subscribers

        Args:
            event: The event to publish
        """
        # Push to event queue
        self.queue.push_event(event)

        # Notify global subscribers
        for handler in self._global_subscribers:
            handler(event)

        # Notify type-specific subscribers
        type_key = event.event_type.value
        if type_key in self._subscribers:
            for event_filter, handler in self._subscribers[type_key]:
                if event_filter is None or event_filter.matches(event):
                    handler(event)

    def publish_event(
        self,
        event_type: EventType,
        source: str,
        payload: dict[str, Any],
        block_height: int,
        timestamp: Optional[int] = None,
    ) -> Event:
        """
        Create and publish an event in one step.

        Args:
            event_type: The canonical event type
            source: The subsystem emitting the event
            payload: The event data
            block_height: The block height at which the event occurred
            timestamp: Unix timestamp (defaults to current time)

        Returns:
            The published Event
        """
        event = self.queue.push(
            event_type=event_type,
            source=source,
            payload=payload,
            block_height=block_height,
            timestamp=timestamp,
        )

        self.publish(event)
        return event

    def get_subscriber_count(self) -> int:
        """Get the total number of registered subscribers."""
        count = len(self._global_subscribers)
        for subscribers in self._subscribers.values():
            count += len(subscribers)
        return count

    def get_event_type_subscriber_count(self, event_type: EventType) -> int:
        """Get the number of subscribers for a specific event type."""
        type_key = event_type.value
        return len(self._subscribers.get(type_key, []))

    def snapshot(self) -> dict[str, Any]:
        """Deterministic event bus snapshot."""
        return {
            "queue": self.queue.snapshot(),
            "registry": self.registry.snapshot(),
            "global_subscribers": len(self._global_subscribers),
            "typed_subscribers": {
                key: len(subs) for key, subs in self._subscribers.items()
            },
            "total_subscribers": self.get_subscriber_count(),
        }

    def reset(self) -> None:
        """Reset the event bus to empty state."""
        self.queue.reset()
        self.registry.reset()
        self._subscribers.clear()
        self._global_subscribers.clear()
