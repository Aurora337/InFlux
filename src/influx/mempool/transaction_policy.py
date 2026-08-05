from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransactionPolicy:
    """
    Rules controlling transaction admission.
    """

    max_pool_size: int = 10000

    minimum_fee: int = 0

    maximum_payload_size: int = 1024

    allow_zero_fee: bool = True

    duplicate_protection: bool = True

    def snapshot(self) -> dict:
        """
        Deterministic policy snapshot.
        """

        return {
            "max_pool_size":
                self.max_pool_size,

            "minimum_fee":
                self.minimum_fee,

            "maximum_payload_size":
                self.maximum_payload_size,

            "allow_zero_fee":
                self.allow_zero_fee,

            "duplicate_protection":
                self.duplicate_protection,
        }