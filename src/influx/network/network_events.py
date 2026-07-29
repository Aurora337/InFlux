from __future__ import annotations

from enum import Enum


class NetworkEventType(str, Enum):
    """
    Deterministic network event identifiers.
    """

    PEER_CONNECTED = "peer_connected"

    PEER_DISCONNECTED = "peer_disconnected"

    MESSAGE_RECEIVED = "message_received"

    MESSAGE_ROUTED = "message_routed"

    SYNC_STARTED = "sync_started"

    SYNC_COMPLETED = "sync_completed"

    REPLICATION_STARTED = "replication_started"

    REPLICATION_COMPLETED = "replication_completed"


class NetworkEvent:
    """
    Deterministic network event container.
    """

    def __init__(
        self,
        event_type: NetworkEventType,
        source: str = "",
        target: str = "",
        metadata: dict | None = None,
    ) -> None:

        self.event_type = event_type

        self.source = source

        self.target = target

        self.metadata = dict(metadata) if metadata is not None else {}


    def snapshot(self) -> dict[str, object]:
        """
        Return deterministic event snapshot.
        """

        return {
            "event_type": self.event_type.value,
            "source": self.source,
            "target": self.target,
            "metadata": dict(self.metadata),
        }
