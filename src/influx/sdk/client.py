from __future__ import annotations

from .config import SDKConfig
from .exceptions import ConnectionFailedError


class InFluxClient:
    """
    High-level SDK client.

    Acts as the primary entry point for
    applications using the InFlux SDK.
    """

    def __init__(
        self,
        config: SDKConfig | None = None,
    ) -> None:

        self.config = config or SDKConfig()

        self.config.validate()

        self._connected = False

    @property
    def connected(self) -> bool:
        """
        Return connection state.
        """

        return self._connected

    def connect(self) -> None:
        """
        Establish a client connection.

        Placeholder implementation until
        the RPC transport layer is integrated.
        """

        if not self.config.host:
            raise ConnectionFailedError(
                "invalid host"
            )

        self._connected = True

    def disconnect(self) -> None:
        """
        Close the client connection.
        """

        self._connected = False

    def ping(self) -> bool:
        """
        Verify connectivity.

        Returns True when connected.
        """

        return self._connected

    @property
    def endpoint(self) -> str:
        """
        Return the configured endpoint.
        """

        return self.config.base_url