class WalletError(Exception):
    """
    Base wallet exception.
    """


class AccountError(WalletError):
    """
    Wallet account failure.
    """


class TransactionError(WalletError):
    """
    Transaction processing failure.
    """


class SigningError(WalletError):
    """
    Signing failure.
    """


class RecoveryError(WalletError):
    """
    Recovery operation failure.
    """