from __future__ import annotations

from .sync_message import SyncMessage
from .sync_metrics import SyncMetrics
from .sync_policy import SyncPolicy
from .sync_request import SyncRequest
from .sync_response import SyncResponse
from .sync_state import SyncState
from .sync_validator import SyncValidator


class Synchronization:
    """
    Core synchronization engine.

    Coordinates synchronization requests,
    responses, and validation.
    """


    def __init__(
        self,
        policy: SyncPolicy | None = None,
    ) -> None:

        self.policy = (
            policy
            if policy is not None
            else SyncPolicy()
        )

        self.validator = SyncValidator(
            self.policy
        )

        self.metrics = SyncMetrics()

        self.state = SyncState.INITIALIZING


    def start(
        self,
    ) -> None:
        """
        Activate synchronization.
        """

        self.state = SyncState.IDLE


    def stop(
        self,
    ) -> None:
        """
        Stop synchronization.
        """

        self.state = SyncState.STOPPED


    def receive_request(
        self,
        request: SyncRequest,
    ) -> bool:
        """
        Receive synchronization request.
        """

        self.metrics.record_request()

        if not self.validator.validate_request(
            request
        ):

            self.metrics.record_validation_failure()

            return False


        self.state = SyncState.RECEIVING

        return True


    def receive_response(
        self,
        response: SyncResponse,
    ) -> bool:
        """
        Receive synchronization response.
        """

        self.metrics.record_response_received()

        if not self.validator.validate_response(
            response
        ):

            self.metrics.record_validation_failure()

            return False


        self.state = SyncState.VERIFYING

        return True


    def validate_message(
        self,
        message: SyncMessage,
    ) -> bool:
        """
        Validate generic sync message.
        """

        return self.validator.validate_message(
            message
        )


    def complete(
        self,
    ) -> None:
        """
        Mark synchronization complete.
        """

        self.state = SyncState.COMPLETE

        self.metrics.record_request_complete()


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic synchronization snapshot.
        """

        return {
            "state":
                self.state.value,

            "metrics":
                self.metrics.snapshot(),
        }