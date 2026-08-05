from __future__ import annotations

from .discovery_policy import DiscoveryPolicy
from .discovery_record import DiscoveryRecord
from .discovery_table import DiscoveryTable


class DiscoveryValidator:
    """
    Validates discovered peers before admission.
    """


    def __init__(
        self,
        policy: DiscoveryPolicy,
        table: DiscoveryTable,
    ) -> None:

        self.policy = policy

        self.table = table


    def validate(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        """
        Validate discovery record.
        """

        if not record.node_id:
            return False

        if not record.address:
            return False

        if record.port < 0:
            return False

        if record.port > 65535:
            return False


        if self.policy.prevent_duplicates:

            if self.table.lookup(
                record.node_id
            ):
                return False


        return self.policy.validate_peer(
            record.trust_score,
            record.active,
        )