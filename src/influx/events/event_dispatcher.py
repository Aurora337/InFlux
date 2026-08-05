"""
Deterministic event dispatcher for the InFlux protocol.

Routes events to registered handlers with ordered delivery,
error isolation, and deterministic processing guarantees.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .event import Event, EventType


EventHandler = Callable[[Event], Any]


@dataclass(slots=True)
class DispatchReceipt:
    """
    Receipt for a dispatched event.

    Records:
    - event identity
    - event type
    - dispatch success
    - handler results
    - failures
    """

    event_id: str
    event_type: EventType
    success: bool

    results: list[Any] = field(default_factory=list)

    error: Optional[str] = None

    handler_count: int = 0
    failure_count: int = 0
    errors: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic receipt snapshot.
        """

        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "success": self.success,
            "results": list(self.results),
            "error": self.error,
            "handler_count": self.handler_count,
            "failure_count": self.failure_count,
            "errors": list(self.errors),
        }


@dataclass(slots=True)
class EventDispatcher:
    """
    Deterministic event dispatcher.

    Features:
    - FIFO handler ordering
    - event-type routing
    - global handlers
    - failure isolation
    - deterministic receipts
    """

    _handlers: dict[str, list[EventHandler]] = field(
        default_factory=dict
    )

    _global_handlers: list[EventHandler] = field(
        default_factory=list
    )

    _handler_order: dict[int, int] = field(
        default_factory=dict
    )

    _order_counter: int = 0


    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        event_type: EventType,
        handler: EventHandler,
    ) -> bool:
        """
        Register a handler for an event type.
        """

        if handler is None:
            return False

        handlers = self._handlers.setdefault(
            event_type.value,
            [],
        )

        if handler in handlers:
            return False

        handlers.append(handler)

        self._handler_order[id(handler)] = (
            self._order_counter
        )

        self._order_counter += 1

        return True


    def register_handler(
        self,
        handler: EventHandler,
        event_type: Optional[EventType] = None,
    ) -> bool:
        """
        Register handler using extended API.
        """

        if handler is None:
            return False


        if event_type is None:

            if handler in self._global_handlers:
                return False

            self._global_handlers.append(handler)

        else:

            return self.register(
                event_type,
                handler,
            )


        self._handler_order[id(handler)] = (
            self._order_counter
        )

        self._order_counter += 1

        return True



    def unregister(
        self,
        event_type: EventType,
    ) -> bool:
        """
        Remove all handlers for event type.
        """

        key = event_type.value

        if key not in self._handlers:
            return False

        del self._handlers[key]

        return True



    def unregister_handler(
        self,
        handler: EventHandler,
        event_type: Optional[EventType] = None,
    ) -> bool:
        """
        Remove specific handler.
        """

        if event_type is None:

            if handler in self._global_handlers:

                self._global_handlers.remove(handler)

                self._handler_order.pop(
                    id(handler),
                    None,
                )

                return True

            return False


        handlers = self._handlers.get(
            event_type.value,
            [],
        )


        if handler not in handlers:
            return False


        handlers.remove(handler)

        self._handler_order.pop(
            id(handler),
            None,
        )

        return True



    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def has_handler(
        self,
        event_type: EventType,
    ) -> bool:
        """
        Check whether event has handlers.
        """

        return bool(
            self._handlers.get(
                event_type.value,
                [],
            )
        )



    def get_handler(
        self,
        event_type: EventType,
    ) -> Optional[EventHandler]:
        """
        Return first handler for event.
        """

        handlers = self._handlers.get(
            event_type.value,
            [],
        )

        if not handlers:
            return None

        return handlers[0]



    def get_registered_types(self) -> list[EventType]:
        """
        Return registered event types.
        """

        return [
            EventType(key)
            for key in self._handlers.keys()
        ]



    # ---------------------------------------------------------
    # Dispatch
    # ---------------------------------------------------------

    def dispatch(
        self,
        event: Event,
        registry: Optional[Any] = None,
    ) -> DispatchReceipt:
        """
        Dispatch an event deterministically.
        """

        # Optional registry validation
        if registry is not None:
            if not registry.validate(event):
                return DispatchReceipt(
                    event_id=event.event_id,
                    event_type=event.event_type,
                    success=False,
                    error="Event registry validation failed",
                    results=[],
                    handler_count=0,
                    failure_count=1,
                    errors=["Event registry validation failed"],
                )

        results: list[Any] = []
        errors: list[str] = []

        handler_count = 0
        failure_count = 0

        handlers: list[EventHandler] = []

        handlers.extend(self._global_handlers)
        handlers.extend(
            self._handlers.get(
                event.event_type.value,
                [],
            )
        )

        # No handlers registered
        if not handlers:
            return DispatchReceipt(
                event_id=event.event_id,
                event_type=event.event_type,
                success=False,
                results=[],
                error="No handler registered",
                handler_count=0,
                failure_count=0,
                errors=["No handler registered"],
            )

        # Dispatch to handlers
        for handler in handlers:
            handler_count += 1

            try:
                results.append(handler(event))

            except Exception as exc:
                failure_count += 1
                errors.append(str(exc))

        successful_handlers = handler_count - failure_count

        return DispatchReceipt(
            event_id=event.event_id,
            event_type=event.event_type,
            success=successful_handlers > 0,
            results=results,
            error=errors[0] if errors else None,
            handler_count=handler_count,
            failure_count=failure_count,
            errors=errors,
        )



    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    def get_handler_count(self) -> int:
        """
        Return total handlers.
        """

        return (
            len(self._global_handlers)
            +
            sum(
                len(h)
                for h in self._handlers.values()
            )
        )


    def handler_count(self) -> int:
        """
        Compatibility alias for tests and protocol API.
        """
        return self.get_handler_count()



    def get_event_type_handler_count(
        self,
        event_type: EventType,
    ) -> int:
        """
        Return handlers for event type.
        """

        return len(
            self._handlers.get(
                event_type.value,
                [],
            )
        )



    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic dispatcher snapshot.
        """

        return {
             "handler_count": self.handler_count(),
             "registered_types": sorted(self._handlers.keys()),
             "global_handlers": len(self._global_handlers),
             "typed_handlers": {
                 key: len(value)
                 for key, value in self._handlers.items()
             },
             "total_handlers": self.get_handler_count(),
             "order_counter": self._order_counter,
        }



    def clear(self) -> None:
        """
        Remove all handlers.
        """

        self._handlers.clear()

        self._global_handlers.clear()

        self._handler_order.clear()

        self._order_counter = 0



    def reset(self) -> None:
        """
        Reset dispatcher.
        """

        self.clear()