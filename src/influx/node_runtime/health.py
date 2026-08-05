from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NodeHealth:
    """
    Node health status.
    """

    online: bool = False
    synced: bool = False
    healthy: bool = False

    def activate(self) -> None:
        self.online = True
        self.healthy = True

    def deactivate(self) -> None:
        self.online = False
        self.healthy = False

    def mark_synced(self) -> None:
        self.synced = True