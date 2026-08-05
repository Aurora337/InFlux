from __future__ import annotations


class NetworkError(Exception):
    """
    Base network exception.
    """


class AddressError(NetworkError):
    """
    Invalid network address.
    """


class PeerError(NetworkError):
    """
    Invalid peer state.
    """


class MessageError(NetworkError):
    """
    Invalid protocol message.
    """


class PeerNotFound(NetworkError):
    """
    Peer not found in registry.
    """


class SessionClosed(NetworkError):
    """
    Session is closed.
    """


class SerializationError(NetworkError):
    """
    Message serialization error.
    """
