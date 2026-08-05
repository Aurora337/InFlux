"""
Testnet exception definitions.
"""


class TestnetError(Exception):
    """
    Base testnet exception.
    """

    __test__ = False


class NodeError(TestnetError):
    """
    Raised when node operations fail.
    """


class NetworkError(TestnetError):
    """
    Raised when network operations fail.
    """


class SimulationError(TestnetError):
    """
    Raised when simulation execution fails.
    """