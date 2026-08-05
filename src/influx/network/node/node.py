from __future__ import annotations

from typing import Optional

from .node_config import NodeConfig
from .node_health import NodeHealth
from .node_identity import NodeIdentity
from .node_lifecycle import NodeLifecycle
from .node_metrics import NodeMetrics
from .node_state import NodeState


class Node:
    """
    Core InFlux network node.

    Coordinates identity, lifecycle, health,
    configuration, and runtime metrics.

    Networking components are attached externally
    to avoid tight coupling between layers.
    """

    def __init__(
        self,
        config: Optional[NodeConfig] = None,
        identity: Optional[NodeIdentity] = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else NodeConfig()
        )

        self.identity = (
            identity
            if identity is not None
            else NodeIdentity()
        )

        self.lifecycle = NodeLifecycle()

        self.health = NodeHealth()

        self.metrics = NodeMetrics()

        self.connections = None

        self.router = None

        self.transport = None


    @property
    def state(self) -> NodeState:
        """
        Current node state.
        """

        return self.lifecycle.state


    def start(self) -> None:
        """
        Start node runtime.
        """

        self.lifecycle.start()

        self.health.state = (
            self.lifecycle.state
        )


    def sync(self) -> None:
        """
        Begin synchronization.
        """

        self.lifecycle.begin_sync()

        self.health.state = (
            self.lifecycle.state
        )


    def activate(self) -> None:
        """
        Activate node.
        """

        self.lifecycle.activate()

        self.health.state = (
            self.lifecycle.state
        )

        self.health.transport_ready = True

        self.health.sync_complete = True


    def stop(self) -> None:
        """
        Stop node runtime.
        """

        self.lifecycle.stop()

        self.health.state = (
            self.lifecycle.state
        )


    def attach_network_components(
        self,
        connections=None,
        router=None,
        transport=None,
    ) -> None:
        """
        Attach network subsystems.

        Components remain optional so nodes can
        operate in simulation environments.
        """

        self.connections = connections

        self.router = router

        self.transport = transport


    def is_ready(self) -> bool:
        """
        Determine network readiness.
        """

        return self.health.ready()


    def is_healthy(self) -> bool:
        """
        Determine operational health.
        """

        return self.health.healthy()


    def snapshot(self) -> dict:
        """
        Deterministic node snapshot.
        """

        return {
            "identity":
                self.identity.snapshot(),

            "config":
                self.config.snapshot(),

            "lifecycle":
                self.lifecycle.snapshot(),

            "health":
                self.health.snapshot(),

            "metrics":
                self.metrics.snapshot(),
        }