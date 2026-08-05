from __future__ import annotations

from .client import InFluxClient
from .exceptions import RPCRequestError
from .models import (
    AccountBalance,
    RPCResponse,
)
from .transactions import (
    SignedTransaction,
    TransactionRequest,
)


class WalletClient:
    """
    High-level wallet interface for the InFlux SDK.

    Provides convenience methods for wallet-related
    RPC operations.
    """

    def __init__(
        self,
        client: InFluxClient,
    ) -> None:
        self._client = client

    def get_balance(
        self,
        address: str,
    ) -> RPCResponse:
        """
        Return the balance for a wallet address.

        Placeholder implementation until live
        RPC integration is available.
        """

        if not self._client.connected:
            raise RPCRequestError(
                "client is not connected"
            )

        return RPCResponse(
            success=True,
            result=AccountBalance(
                address=address,
                confirmed=0,
                pending=0,
            ),
        )

    def build_transaction(
        self,
        sender: str,
        recipient: str,
        amount: int,
        fee: int = 0,
    ) -> TransactionRequest:
        """
        Construct a transaction request.
        """

        return TransactionRequest(
            sender=sender,
            recipient=recipient,
            amount=amount,
            fee=fee,
        )

    def sign_transaction(
        self,
        request: TransactionRequest,
        signature: str,
    ) -> SignedTransaction:
        """
        Produce a signed transaction.

        Placeholder until cryptographic signing
        is integrated with the Identity package.
        """

        tx_id = f"{request.sender}:{request.recipient}:{request.amount}"

        return SignedTransaction(
            tx_id=tx_id,
            request=request,
            signature=signature,
        )