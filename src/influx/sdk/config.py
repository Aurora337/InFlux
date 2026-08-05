from __future__ import annotations

from dataclasses import dataclass

from .exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class SDKConfig:
    """
    SDK configuration.
    """

    host: str = "127.0.0.1"

    port: int = 8080

    use_tls: bool = False

    timeout: float = 30.0

    def validate(self) -> None:
        """
        Validate configuration.
        """

        if not self.host:
            raise ConfigurationError(
                "host must not be empty"
            )

        if self.port <= 0:
            raise ConfigurationError(
                "port must be greater than zero"
            )

        if self.timeout <= 0:
            raise ConfigurationError(
                "timeout must be greater than zero"
            )

    @property
    def base_url(self) -> str:
        """
        Return the RPC base URL.
        """

        scheme = "https" if self.use_tls else "http"

        return f"{scheme}://{self.host}:{self.port}"