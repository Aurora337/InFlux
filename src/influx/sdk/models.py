from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RPCResponse:
    """
    Generic RPC response.
    """

    success: bool

    result: object | None = None

    error: str | None = None


@dataclass(frozen=True, slots=True)
class NetworkInfo:
    """
    Basic network information.
    """

    chain_id: str

    protocol_version: str

    peer_count: int = 0

    block_height: int = 0


@dataclass(frozen=True, slots=True)
class AccountBalance:
    """
    Wallet balance information.
    """

    address: str

    confirmed: int = 0

    pending: int = 0


@dataclass(frozen=True, slots=True)
class TransactionReceipt:
    """
    Transaction execution receipt.
    """

    tx_id: str

    accepted: bool

    message: str = ""

    metadata: dict[str, object] = field(
        default_factory=dict,
    )