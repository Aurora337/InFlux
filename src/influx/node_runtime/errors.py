from __future__ import annotations


class NodeRuntimeError(Exception):
    """
    Base node runtime exception.
    """


class NodeConfigurationError(NodeRuntimeError):
    """
    Raised when node configuration is invalid.
    """


class NodeIdentityError(NodeRuntimeError):
    """
    Raised when node identity operations fail.
    """


class NodeHealthError(NodeRuntimeError):
    """
    Raised when node health checks fail.
    """


class NodeLifecycleError(NodeRuntimeError):
    """
    Raised during node lifecycle failures.
    """