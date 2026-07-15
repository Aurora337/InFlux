from __future__ import annotations


class RuntimeErrorBase(Exception):
    """
    Base exception for runtime execution failures.
    """


class ExecutionError(RuntimeErrorBase):
    """
    Raised when runtime execution fails.
    """


class ContextError(RuntimeErrorBase):
    """
    Raised when execution context operations fail.
    """


class StateTransitionError(RuntimeErrorBase):
    """
    Raised when runtime state transition fails.
    """