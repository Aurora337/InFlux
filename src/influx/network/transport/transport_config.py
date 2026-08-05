from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransportConfig:
    """
    Transport configuration.
    """

    host: str
    port: int

    timeout: int = 30
    max_connections: int = 64

    def validate(self) -> None:
        """
        Validate transport configuration.
        """

        if not self.host:
            raise ValueError(
                "missing transport host"
            )

        if self.port <= 0:
            raise ValueError(
                "invalid transport port"
            )

        if self.port > 65535:
            raise ValueError(
                "invalid transport port"
            )

        if self.timeout <= 0:
            raise ValueError(
                "invalid timeout"
            )

        if self.max_connections <= 0:
            raise ValueError(
                "invalid max connections"
            )