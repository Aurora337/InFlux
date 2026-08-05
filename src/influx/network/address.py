from __future__ import annotations

from dataclasses import dataclass

from .errors import AddressError


@dataclass(slots=True)
class NetworkAddress:
    """
    Deterministic network endpoint.
    """

    host: str
    port: int

    def validate(self) -> None:
        """
        Validate address.
        """

        if not self.host:
            raise AddressError(
                "host cannot be empty"
            )

        if self.port <= 0:
            raise AddressError(
                "invalid port"
            )

    @property
    def endpoint(self) -> str:
        """
        Return host:port.
        """

        return f"{self.host}:{self.port}"