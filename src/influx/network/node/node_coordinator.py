from __future__ import annotations

from dataclasses import dataclass

from .network_node import NetworkNode
from .node_events import NodeEvents
from .node_event import NodeEvent
from .node_sync import NodeSync
from .node_validator import NodeValidator


@dataclass(slots=True)
class NodeCoordinator:
    """
    Coordinates deterministic node operation.
    """

    validator: NodeValidator
    events: NodeEvents
    sync: NodeSync


    def start(
        self,
        node: NetworkNode,
        timestamp: int,
    ) -> bool:
        """
        Start node coordination.
        """

        if not self.validator.validate(node):
            return False

        node.start()

        self.events.record(
            NodeEvent(
                event_type="START",
                node_id=node.node_id,
                timestamp=timestamp,
                details={
                    "status": "running"
                },
            )
        )

        return True


    def stop(
        self,
        node: NetworkNode,
        timestamp: int,
    ) -> None:
        """
        Stop node coordination.
        """

        node.stop()

        self.events.record(
            NodeEvent(
                event_type="STOP",
                node_id=node.node_id,
                timestamp=timestamp,
                details={
                    "status": "stopped"
                },
            )
        )


    def synchronize(
        self,
        target_height: int,
    ) -> None:
        """
        Begin node synchronization.
        """

        self.sync.start(
            target_height
        )