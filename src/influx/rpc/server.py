from __future__ import annotations

from typing import Any, Callable

from .api import (
    RPCRequest,
    RPCResponse,
)

from .exceptions import (
    MethodNotFoundError,
)


class RPCServer:
    """
    Deterministic RPC server.

    Maintains registered methods and
    executes incoming requests.
    """

    def __init__(
        self,
    ) -> None:

        self._methods: dict[
            str,
            Callable[..., Any],
        ] = {}

    def register_method(
        self,
        name: str,
        handler: Callable[..., Any],
    ) -> None:
        """
        Register RPC method.
        """

        self._methods[name] = handler

    def handle(
        self,
        request: RPCRequest,
    ) -> RPCResponse:
        """
        Process RPC request.
        """

        if request.method not in self._methods:

            raise MethodNotFoundError(
                request.method
            )

        handler = self._methods[
            request.method
        ]

        result = handler(
            **request.params
        )

        return RPCResponse(
            request_id=request.request_id,
            result=result,
        )