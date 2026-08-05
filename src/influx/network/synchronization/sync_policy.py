from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyncPolicy:
    """
    Rules controlling synchronization behavior.
    """

    max_payload_size: int = 1024 * 1024

    require_signature: bool = False

    allow_empty_state: bool = False

    max_range_size: int = 10000


    def validate_request(
        self,
        requester: str,
        target: str,
        range_start: int,
        range_end: int,
    ) -> bool:
        """
        Validate synchronization request.
        """

        if not requester:
            return False

        if not target:
            return False

        if range_start < 0:
            return False

        if range_end < range_start:
            return False

        if (
            range_end - range_start
            > self.max_range_size
        ):
            return False

        return True


    def validate_response(
        self,
        payload_size: int,
        signature: str,
    ) -> bool:
        """
        Validate synchronization response.
        """

        if payload_size > self.max_payload_size:
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
            "max_payload_size":
                self.max_payload_size,

            "require_signature":
                self.require_signature,

            "allow_empty_state":
                self.allow_empty_state,

            "max_range_size":
                self.max_range_size,
        }