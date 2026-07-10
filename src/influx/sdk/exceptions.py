"""
InFlux SDK exception definitions.
"""


class SDKError(Exception):
    """
    Base SDK exception.
    """


class ConfigurationError(SDKError):
    """
    Raised when SDK configuration is invalid.
    """


class RPCRequestError(SDKError):
    """
    Raised when an RPC request fails.
    """


class ConnectionFailedError(SDKError):
    """
    Raised when the SDK cannot establish a connection.
    """