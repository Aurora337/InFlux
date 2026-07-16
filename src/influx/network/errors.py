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