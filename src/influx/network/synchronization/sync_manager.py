from __future__ import annotations

from typing import Dict, Optional

from .synchronization import Synchronization
from .sync_request import SyncRequest
from .sync_response import SyncResponse


class SyncManager:
    """
    Manages multiple synchronization domains.
    """


    def __init__(
        self,
    ) -> None:

        self.instances: Dict[
            str,
            Synchronization,
        ] = {}


    def register(
        self,
        name: str,
        synchronization: Synchronization,
    ) -> None:
        """
        Register synchronization service.
        """

        self.instances[name] = synchronization


    def lookup(
        self,
        name: str,
    ) -> Optional[Synchronization]:
        """
        Find synchronization service.
        """

        return self.instances.get(
            name
        )


    def receive_request(
        self,
        name: str,
        request: SyncRequest,
    ) -> bool:
        """
        Route sync request.
        """

        sync = self.lookup(
            name
        )

        if sync is None:
            return False

        return sync.receive_request(
            request
        )


    def receive_response(
        self,
        name: str,
        response: SyncResponse,
    ) -> bool:
        """
        Route sync response.
        """

        sync = self.lookup(
            name
        )

        if sync is None:
            return False

        return sync.receive_response(
            response
        )


    def start_all(
        self,
    ) -> None:
        """
        Start all synchronization services.
        """

        for sync in self.instances.values():

            sync.start()


    def stop_all(
        self,
    ) -> None:
        """
        Stop all synchronization services.
        """

        for sync in self.instances.values():

            sync.stop()


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic manager snapshot.
        """

        return {
            name:
                sync.snapshot()

            for name, sync
            in self.instances.items()
        }