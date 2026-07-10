from __future__ import annotations


class NetworkError(Exception):
    """Base networking exception."""


class PeerNotFound(NetworkError):
    """Raised when a peer cannot be located."""


class SessionClosed(NetworkError):
    """Raised when attempting to use a closed session."""


class SerializationError(NetworkError):
    """Raised when serialization fails."""