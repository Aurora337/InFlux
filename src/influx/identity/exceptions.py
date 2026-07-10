class IdentityError(Exception):
    """
    Base identity subsystem error.
    """


class IdentityNotFoundError(
    IdentityError,
):
    """
    Raised when identity does not exist.
    """


class InvalidSignatureError(
    IdentityError,
):
    """
    Raised when signature validation fails.
    """


class CertificateError(
    IdentityError,
):
    """
    Raised when certificate validation fails.
    """


class KeyRotationError(
    IdentityError,
):
    """
    Raised during failed key rotation.
    """