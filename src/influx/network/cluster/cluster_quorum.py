from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterQuorum:
    """
    Determines deterministic quorum status with BFT awareness.

    Features:
    - Standard majority quorum (n/2 + 1)
    - BFT quorum (2f + 1 where f = (n-1)//3)
    - Supermajority threshold (2/3)
    - Quorum intersection validation
    - Dynamic quorum size calculation
    """

    required: int = 0
    total: int = 0
    present: int = 0
    bft_enabled: bool = True

    def required_standard(self) -> int:
        """Standard majority quorum (n/2 + 1)."""
        return (self.total // 2) + 1

    def required_bft(self) -> int:
        """BFT quorum size (2f + 1)."""
        if not self.bft_enabled:
            return self.required_standard()

        f = (self.total - 1) // 3
        return 2 * f + 1

    def required_supermajority(self) -> int:
        """Supermajority threshold (ceil(2n/3))."""
        return (2 * self.total + 2) // 3

    def calculate_required(self) -> int:
        """
        Calculate quorum requirement.

        Explicit required values supplied during construction
        override automatic calculation.
        """
        if self.required > 0:
            return self.required

        if self.total <= 0:
            return 0

        return (
            self.required_bft()
            if self.bft_enabled
            else self.required_standard()
        )

    def reached(self) -> bool:
        """Check whether quorum has been reached."""
        required = self.calculate_required()

        if required == 0:
            return False

        return self.present >= required

    def has_supermajority(self) -> bool:
        """Check if supermajority is reached."""
        return self.present >= self.required_supermajority()

    def quorum_intersection(
        self,
        quorum_a: int,
        quorum_b: int,
    ) -> bool:
        """
        Validate that two quorums intersect.

        For BFT safety, any two quorums must intersect
        in at least one honest node.
        """
        intersection = quorum_a + quorum_b - self.total
        return intersection >= 1

    def remaining_needed(self) -> int:
        """Return additional nodes needed to reach quorum."""
        needed = self.calculate_required() - self.present
        return max(needed, 0)

    def snapshot(self) -> dict[str, int | bool | float]:
        return {
            "total": self.total,
            "present": self.present,
            "required": self.calculate_required(),
            "required_standard": self.required_standard(),
            "required_bft": self.required_bft(),
            "required_supermajority": self.required_supermajority(),
            "reached": self.reached(),
            "supermajority": self.has_supermajority(),
            "remaining_needed": self.remaining_needed(),
            "bft_enabled": self.bft_enabled,
        }