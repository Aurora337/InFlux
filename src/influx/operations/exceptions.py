"""
Operations layer exception definitions.
"""


class OperationsError(Exception):
    """
    Base operations exception.
    """


class HealthError(OperationsError):
    """
    Raised when health checks fail.
    """


class MonitoringError(OperationsError):
    """
    Raised when monitoring fails.
    """


class AlertError(OperationsError):
    """
    Raised when alert processing fails.
    """