from __future__ import annotations

from typing import Callable, Any

from .api import (
    RPCRequest,
    RPCResponse,
)


class RPCClient:
    """
    RPC client interface.

    Provides request construction and
    response handling.
    """

    def __init__(
        self,
        transport: Callable[
            [RPCRequest],
            RPCResponse,
        ],
    ) -> None:

        self._transport = transport

    def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        request_id: str = "0",
    ) -> RPCResponse:
        """
        Execute RPC call.
        """

        request = RPCRequest(
            method=method,
            params=params or {},
            request_id=request_id,
        )

        return self._transport(
            request
        )