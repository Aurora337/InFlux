from __future__ import annotations

from .discovery_metrics import DiscoveryMetrics
from .discovery_policy import DiscoveryPolicy
from .discovery_record import DiscoveryRecord
from .discovery_state import DiscoveryState
from .discovery_table import DiscoveryTable
from .discovery_validator import DiscoveryValidator


class Discovery:
    """
    Core peer discovery engine.

    Responsible for maintaining discovered peer
    knowledge and applying discovery rules.
    """

    def __init__(
        self,
        policy: DiscoveryPolicy | None = None,
    ) -> None:

        self.policy = (
            policy
            if policy is not None
            else DiscoveryPolicy()
        )

        self.table = DiscoveryTable()

        self.validator = DiscoveryValidator(
            self.policy,
            self.table,
        )

        self.metrics = DiscoveryMetrics()

        self.state = DiscoveryState.INITIALIZING


    def start(self) -> None:
        """
        Start discovery service.
        """

        self.state = DiscoveryState.DISCOVERING


    def stop(self) -> None:
        """
        Stop discovery service.
        """

        self.state = DiscoveryState.STOPPED


    def discover(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        """
        Attempt to add discovered peer.
        """

        self.metrics.record_attempt()

        if not self.validator.validate(record):

            self.metrics.record_rejected()

            return False


        added = self.table.add(
            record
        )

        if added:

            self.metrics.record_discovered()

            self.state = DiscoveryState.ACTIVE

            return True


        self.metrics.record_rejected()

        return False


    def remove(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove discovered peer.
        """

        removed = self.table.remove(
            node_id
        )

        if removed:

            self.metrics.record_removed()

        return removed


    def lookup(
        self,
        node_id: str,
    ) -> DiscoveryRecord | None:
        """
        Lookup peer.
        """

        return self.table.lookup(
            node_id
        )


    def snapshot(self) -> dict:
        """
        Deterministic discovery snapshot.
        """

        return {
            "state":
                self.state.value,

            "table":
                self.table.snapshot(),

            "metrics":
                self.metrics.snapshot(),
        }