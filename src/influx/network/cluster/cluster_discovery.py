from __future__ import annotations

from dataclasses import dataclass, field

from .cluster_member import ClusterMember


@dataclass(slots=True)
class ClusterDiscovery:
    """
    Tracks discovered cluster members.
    """

    _discovered: dict[str, ClusterMember] = field(
        default_factory=dict
    )

    def discover(
        self,
        member: ClusterMember,
    ) -> bool:
        """
        Register a discovered member.
        """

        if member.node_id in self._discovered:
            return False

        self._discovered[member.node_id] = member
        return True

    def get(
        self,
        node_id: str,
    ) -> ClusterMember | None:
        """
        Retrieve a discovered member.
        """

        return self._discovered.get(node_id)

    def members(
        self,
    ) -> list[ClusterMember]:
        """
        Return all discovered members.
        """

        return list(self._discovered.values())

    def clear(
        self,
    ) -> None:
        """
        Clear discovery cache.
        """

        self._discovered.clear()