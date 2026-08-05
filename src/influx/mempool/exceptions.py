"""
Mempool exception definitions.
"""


class MempoolError(Exception):
    """
    Base mempool exception.
    """


class InvalidTransactionError(MempoolError):
    """
    Raised when a transaction is invalid.
    """


class DuplicateTransactionError(MempoolError):
    """
    Raised when a transaction already exists.
    """


class TransactionNotFoundError(MempoolError):
    """
    Raised when a transaction cannot be found.
    """