from __future__ import annotations

from .client import InFluxClient
from .exceptions import RPCRequestError
from .models import (
    NetworkInfo,
    RPCResponse,
    TransactionReceipt,
)
from .transactions import SignedTransaction


class RPCClient:
    """
    High-level RPC interface for the SDK.
    """

    def __init__(
        self,
        client: InFluxClient,
    ) -> None:

        self._client = client

    def get_network_info(
        self,
    ) -> RPCResponse:
        """
        Return placeholder network information.
        """

        if not self._client.connected:
            raise RPCRequestError(
                "client is not connected"
            )

        return RPCResponse(
            success=True,
            result=NetworkInfo(
                chain_id="influx",
                protocol_version="1.0",
            ),
        )

    def submit_transaction(
        self,
        transaction: SignedTransaction,
    ) -> RPCResponse:
        """
        Submit a signed transaction.

        Placeholder implementation until
        live RPC integration is available.
        """

        if not self._client.connected:
            raise RPCRequestError(
                "client is not connected"
            )

        return RPCResponse(
            success=True,
            result=TransactionReceipt(
                tx_id=transaction.tx_id,
                accepted=True,
                message="accepted",
            ),
        )