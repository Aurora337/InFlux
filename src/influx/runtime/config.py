from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class RuntimeConfig:
    """
    Runtime configuration for an InFlux node.
    """

    node_name: str = "influx-node"

    host: str = "127.0.0.1"

    port: int = 9000

    rpc_enabled: bool = True

    rpc_port: int = 8080

    metrics_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RuntimeConfig":
        """
        Create configuration from dictionary.
        """
        return cls(**data)