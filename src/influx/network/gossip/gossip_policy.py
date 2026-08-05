from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GossipPolicy:
    """
    Rules controlling gossip propagation.
    """

    max_ttl: int = 8

    max_messages: int = 10000

    require_signature: bool = False

    prevent_duplicates: bool = True

    max_hops: int = 16


    def validate_message(
        self,
        ttl: int,
        hops: int,
        signature: str,
    ) -> bool:
        """
        Validate gossip message admission.
        """

        if ttl < 0:
            return False

        if ttl > self.max_ttl:
            return False

        if hops > self.max_hops:
            return False

        if (
            self.require_signature
            and not signature
        ):
            return False

        return True


    def snapshot(self) -> dict:
        """
        Deterministic policy snapshot.
        """

        return {
            "max_ttl":
                self.max_ttl,

            "max_messages":
                self.max_messages,

            "require_signature":
                self.require_signature,

            "prevent_duplicates":
                self.prevent_duplicates,

            "max_hops":
                self.max_hops,
        }