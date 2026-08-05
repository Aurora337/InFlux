from __future__ import annotations

from dataclasses import dataclass

from .configuration import NodeConfiguration
from .health import NodeHealth
from .identity import NodeIdentity


@dataclass(slots=True)
class RuntimeNode:
    """
    Live InFlux runtime node.
    """

    configuration: NodeConfiguration
    identity: NodeIdentity
    health: NodeHealth

    def start(self) -> None:
        """
        Start node.
        """

        self.configuration.validate()
        self.identity.validate()

        self.health.activate()

    def stop(self) -> None:
        """
        Stop node.
        """

        self.health.deactivate()

    def is_ready(self) -> bool:
        """
        Determine node readiness.
        """

        return (
            self.health.online
            and self.health.healthy
            and self.health.synced
        )