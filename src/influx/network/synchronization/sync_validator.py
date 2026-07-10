from __future__ import annotations

from .sync_message import SyncMessage
from .sync_policy import SyncPolicy
from .sync_request import SyncRequest
from .sync_response import SyncResponse


class SyncValidator:
    """
    Validates synchronization exchanges.
    """


    def __init__(
        self,
        policy: SyncPolicy,
    ) -> None:

        self.policy = policy


    def validate_request(
        self,
        request: SyncRequest,
    ) -> bool:
        """
        Validate incoming request.
        """

        return self.policy.validate_request(
            requester=request.requester,
            target=request.target,
            range_start=request.range_start,
            range_end=request.range_end,
        )


    def validate_response(
        self,
        response: SyncResponse,
    ) -> bool:
        """
        Validate synchronization response.
        """

        payload_size = len(
            str(response.payload)
        )

        return self.policy.validate_response(
            payload_size,
            response.signature,
        )


    def validate_message(
        self,
        message: SyncMessage,
    ) -> bool:
        """
        Validate generic sync message.
        """

        if not message.source_node:
            return False

        if not message.target_node:
            return False

        return True