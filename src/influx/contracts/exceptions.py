"""
Smart contract runtime exceptions.
"""


class ContractError(Exception):
    """Base contract exception."""


class ContractExecutionError(ContractError):
    """Raised when contract execution fails."""


class ContractRegistrationError(ContractError):
    """Raised when contract registration fails."""


class GasExhaustedError(ContractError):
    """Raised when gas limit is exceeded."""