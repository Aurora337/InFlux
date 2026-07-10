class RPCError(Exception):
    """
    Base RPC exception.
    """


class InvalidRequestError(RPCError):
    """
    Raised when an RPC request is invalid.
    """


class MethodNotFoundError(RPCError):
    """
    Raised when an RPC method does not exist.
    """


class InvalidResponseError(RPCError):
    """
    Raised when an RPC response is invalid.
    """


class ConnectionError(RPCError):
    """
    Raised when RPC communication fails.
    """