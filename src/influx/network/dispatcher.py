from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from influx.network.message import NetworkMessage

MessageHandler = Callable[[NetworkMessage], None]


@dataclass(slots=True)
class MessageDispatcher:
    """
    Deterministic dispatcher for network messages.
    """

    _handlers: dict[str, MessageHandler] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def register(
        self,
        message_type: str,
        handler: MessageHandler,
    ) -> None:
        """
        Register a handler for a message type.
        """

        self._handlers[message_type] = handler

    def unregister(
        self,
        message_type: str,
    ) -> None:
        """
        Remove a registered handler.
        """

        self._handlers.pop(message_type, None)

    def dispatch(
        self,
        message: NetworkMessage,
    ) -> bool:
        """
        Dispatch a message to its registered handler.

        Returns True if a handler was found.
        """

        handler = self._handlers.get(
            message.message_type
        )

        if handler is None:
            return False

        handler(message)

        return True

    def handler_count(
        self,
    ) -> int:
        """
        Return the number of registered handlers.
        """

        return len(self._handlers)

    def clear(
        self,
    ) -> None:
        """
        Remove every registered handler.
        """

        self._handlers.clear()