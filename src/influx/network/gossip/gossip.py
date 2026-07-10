from __future__ import annotations

from .gossip_message import GossipMessage
from .gossip_metrics import GossipMetrics
from .gossip_policy import GossipPolicy
from .gossip_state import GossipState
from .gossip_table import GossipTable
from .gossip_validator import GossipValidator


class Gossip:
    """
    Core gossip propagation engine.

    Handles message admission, storage,
    and propagation lifecycle.
    """

    def __init__(
        self,
        policy: GossipPolicy | None = None,
    ) -> None:

        self.policy = (
            policy
            if policy is not None
            else GossipPolicy()
        )

        self.table = GossipTable()

        self.validator = GossipValidator(
            self.policy,
            self.table,
        )

        self.metrics = GossipMetrics()

        self.state = GossipState.INITIALIZING


    def start(self) -> None:
        """
        Activate gossip service.
        """

        self.state = GossipState.ACTIVE


    def stop(self) -> None:
        """
        Stop gossip service.
        """

        self.state = GossipState.STOPPED


    def receive(
        self,
        message: GossipMessage,
    ) -> bool:
        """
        Receive a gossip message.
        """

        self.metrics.record_received()

        if not self.validator.validate(
            message
        ):

            self.metrics.record_rejected()

            return False


        added = self.table.add(
            message
        )

        if not added:

            self.metrics.record_rejected()

            return False


        self.state = GossipState.PROPAGATING

        self.metrics.record_propagated()

        return True


    def propagate(
        self,
        message: GossipMessage,
    ) -> bool:
        """
        Prepare message for forwarding.
        """

        if message.expired():

            self.metrics.record_expired()

            return False


        return self.receive(
            message
        )


    def lookup(
        self,
        message_id: str,
    ) -> GossipMessage | None:
        """
        Retrieve known message.
        """

        return self.table.lookup(
            message_id
        )


    def snapshot(self) -> dict:
        """
        Deterministic gossip snapshot.
        """

        return {
            "state":
                self.state.value,

            "table":
                self.table.snapshot(),

            "metrics":
                self.metrics.snapshot(),
        }