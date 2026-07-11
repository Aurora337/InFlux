from __future__ import annotations

from dataclasses import dataclass, field

from .exceptions import NodeError


@dataclass(slots=True)
class TestnetNode:
    """
    Deterministic testnet node representation.
    """

    node_id: str

    validator: bool = False

    online: bool = False

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    def start(self) -> None:
        """
        Start the node.
        """

        if not self.node_id:
            raise NodeError(
                "node id required"
            )

        self.online = True

    def stop(self) -> None:
        """
        Stop the node.
        """

        self.online = False

    def status(self) -> str:
        """
        Return node status.
        """

        return (
            "online"
            if self.online
            else "offline"
        )