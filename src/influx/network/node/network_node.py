from __future__ import annotations

from dataclasses import dataclass, field

from .node_config import NodeConfig
from .node_state import NodeState


@dataclass(slots=True)
class NetworkNode:
    """
    Deterministic network node.
    """

    node_id: str

    config: NodeConfig

    state: NodeState = field(
        default=NodeState.CREATED
    )

    def start(self) -> None:
        """
        Start the node.
        """

        self.state = NodeState.ACTIVE

    def stop(self) -> None:
        """
        Stop the node.
        """

        self.state = NodeState.STOPPED

    def is_running(self) -> bool:
        """
        Return current node state.
        """

        return self.state == NodeState.ACTIVE