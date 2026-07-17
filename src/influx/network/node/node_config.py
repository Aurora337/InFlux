from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NodeConfig:
    """
    Network node configuration.
    """

    host: str = "127.0.0.1"

    port: int = 9000

    max_peers: int = 64

    def validate(self) -> None:
        if not self.host:
            raise ValueError("host required")

        if self.port <= 0:
            raise ValueError("invalid port")

        if self.port > 65535:
            raise ValueError("invalid port")
        
        if self.max_peers <=0:
            raise ValueError("invalid max peers")
        
    def snapshot(self) -> dict[str, int | str]:
        """
        Deterministic configuration snapshot.
        """

        return {
            "host": self.host,
            "port": self.port,
            "max_peers": self.max_peers,
        }