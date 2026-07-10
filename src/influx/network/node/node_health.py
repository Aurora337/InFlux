from __future__ import annotations

from dataclasses import dataclass

from .node_state import NodeState


@dataclass(slots=True)
class NodeHealth:
    """
    Determines node readiness and operational health.
    """

    state: NodeState = NodeState.CREATED

    peers_available: bool = False

    transport_ready: bool = False

    sync_complete: bool = False


    def healthy(self) -> bool:
        """
        Determine if node is operational.
        """

        return (
            self.state == NodeState.ACTIVE
            and self.transport_ready
            and self.sync_complete
        )


    def ready(self) -> bool:
        """
        Determine whether node may join network.
        """

        return (
            self.transport_ready
            and self.state != NodeState.FAILED
        )


    def snapshot(self) -> dict:
        """
        Deterministic health snapshot.
        """

        return {
            "state":
                self.state.value,

            "peers_available":
                self.peers_available,

            "transport_ready":
                self.transport_ready,

            "sync_complete":
                self.sync_complete,

            "healthy":
                self.healthy(),

            "ready":
                self.ready(),
        }