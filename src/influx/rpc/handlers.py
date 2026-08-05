from __future__ import annotations

from typing import Any, Callable


class RPCHandlerRegistry:
    """
    Registry for RPC callable methods.

    Provides a deterministic mapping between
    RPC method names and execution handlers.
    """

    def __init__(
        self,
    ) -> None:

        self._handlers: dict[
            str,
            Callable[..., Any],
        ] = {}

    def register(
        self,
        method: str,
        handler: Callable[..., Any],
    ) -> None:
        """
        Register RPC handler.
        """

        self._handlers[
            method
        ] = handler

    def unregister(
        self,
        method: str,
    ) -> bool:
        """
        Remove RPC handler.
        """

        if method in self._handlers:

            del self._handlers[
                method
            ]

            return True

        return False

    def exists(
        self,
        method: str,
    ) -> bool:
        """
        Determine whether handler exists.
        """

        return method in self._handlers

    def get(
        self,
        method: str,
    ) -> Callable[..., Any]:
        """
        Retrieve handler.
        """

        return self._handlers[
            method
        ]

    def methods(
        self,
    ) -> list[str]:
        """
        Return registered methods.
        """

        return list(
            self._handlers.keys()
        )