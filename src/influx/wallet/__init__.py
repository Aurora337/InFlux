"""
InFlux Wallet Protocol.

Provides:

- wallet accounts
- addresses
- transactions
- signing
- recovery
"""

from .accounts import (
    WalletAccount,
)

from .addresses import (
    WalletAddress,
    AddressManager,
)

from .transactions import (
    WalletTransaction,
    TransactionInput,
    TransactionOutput,
)

from .signing import (
    WalletSigner,
)

from .recovery import (
    RecoveryRecord,
    RecoveryManager,
)

from .exceptions import (
    WalletError,
    AccountError,
    TransactionError,
    SigningError,
    RecoveryError,
)


__all__ = [
    "WalletAccount",
    "WalletAddress",
    "AddressManager",
    "WalletTransaction",
    "TransactionInput",
    "TransactionOutput",
    "WalletSigner",
    "RecoveryRecord",
    "RecoveryManager",
    "WalletError",
    "AccountError",
    "TransactionError",
    "SigningError",
    "RecoveryError",
]