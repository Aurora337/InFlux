from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .transport_type import TransportType


@dataclass(slots=True)
class TransportConfig:
    """
    Configuration for a transport endpoint.

    This object is intentionally transport-neutral so
    future adapters can interpret additional options.
    """

    transport_type: TransportType = (
        TransportType.LOCAL
    )

    host: str = "127.0.0.1"

    port: int = 0

    timeout: float = 30.0

    max_connections: int = 64

    secure: bool = False

    options: dict[str, Any] = field(
        default_factory=dict
    )


    def validate(self) -> bool:
        """
        Validate configuration values.
        """

        if self.port < 0:
            return False

        if self.port > 65535:
            return False

        if self.timeout <= 0:
            return False

        if self.max_connections <= 0:
            return False

        return True


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic configuration snapshot.
        """

        return {
            "transport_type":
                self.transport_type.value,

            "host":
                self.host,

            "port":
                self.port,

            "timeout":
                self.timeout,

            "max_connections":
                self.max_connections,

            "secure":
                self.secure,

            "options":
                dict(self.options),
        }