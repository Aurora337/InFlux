from __future__ import annotations

from dataclasses import dataclass

from .errors import NodeConfigurationError


@dataclass(slots=True)
class NodeConfiguration:
    """
    Deterministic node runtime configuration.
    """

    node_id: str
    network: str
    role: str = "validator"
    enabled: bool = True

    def validate(self) -> None:
        """
        Validate node configuration.
        """

        if not self.node_id:
            raise NodeConfigurationError(
                "node id required"
            )

        if not self.network:
            raise NodeConfigurationError(
                "network required"
            )