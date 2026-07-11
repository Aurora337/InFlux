from __future__ import annotations

from dataclasses import dataclass

from .exceptions import GasExhaustedError


@dataclass(slots=True)
class GasMeter:
    """
    Deterministic gas accounting.
    """

    limit: int

    consumed: int = 0

    def consume(
        self,
        amount: int,
    ) -> None:
        """
        Consume gas units.
        """

        if amount < 0:
            raise ValueError(
                "Gas amount cannot be negative."
            )

        if self.consumed + amount > self.limit:
            raise GasExhaustedError(
                "Gas limit exceeded."
            )

        self.consumed += amount

    def remaining(self) -> int:
        """
        Return remaining gas.
        """

        return self.limit - self.consumed

    def exhausted(self) -> bool:
        """
        Determine whether gas is exhausted.
        """

        return self.consumed >= self.limit