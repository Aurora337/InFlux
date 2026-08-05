from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveryPolicy:
    """
    Rules controlling peer discovery.

    Policies allow the network to evolve without
    changing discovery mechanics.
    """

    max_peers: int = 64

    minimum_trust_score: float = 0.0

    require_active: bool = True

    prefer_validators: bool = True

    prevent_duplicates: bool = True


    def validate_peer(
        self,
        trust_score: float,
        active: bool,
    ) -> bool:
        """
        Validate whether a peer meets policy.
        """

        if self.require_active and not active:
            return False

        if trust_score < self.minimum_trust_score:
            return False

        return True


    def snapshot(self) -> dict:
        """
        Deterministic policy snapshot.
        """

        return {
            "max_peers": self.max_peers,

            "minimum_trust_score":
                self.minimum_trust_score,

            "require_active":
                self.require_active,

            "prefer_validators":
                self.prefer_validators,

            "prevent_duplicates":
                self.prevent_duplicates,
        }