"""
Transport exception definitions.
"""


class TransportError(Exception):
    """
    Base transport exception.
    """


class ConnectionError(TransportError):
    """
    Raised when a transport connection fails.
    """


class ProtocolError(TransportError):
    """
    Raised when a transport message is invalid.
    """


class MessageValidationError(ProtocolError):
    """
    Raised when message validation fails.
    """