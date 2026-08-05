from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any
from uuid import uuid4

from .message_type import MessageType


@dataclass(slots=True)
class Message:
    """
    Canonical network message exchanged throughout the InFlux protocol.

    This object is intentionally transport-independent. Whether a
    message travels over TCP, QUIC, WebSockets, local simulation, or
    future transports, the logical message remains identical.

    Every message should be deterministic after construction so that
    replay, auditing, and consensus verification produce identical
    results across all participating nodes.
    """

    #
    # Identity
    #

    message_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    correlation_id: str | None = None

    #
    # Protocol
    #

    protocol_version: str = "1.0"

    message_type: MessageType = MessageType.CUSTOM

    #
    # Routing
    #

    source: str = ""

    destination: str = ""

    sequence: int = 0

    ttl: int = 16

    priority: int = 0

    #
    # Payload
    #

    payload: dict[str, Any] = field(
        default_factory=dict
    )

    #
    # Metadata
    #

    timestamp: float = field(
        default_factory=time
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    #
    # Lifecycle
    #

    delivered: bool = False

    acknowledged: bool = False

    dropped: bool = False


    def decrement_ttl(self) -> bool:
        """
        Consume one network hop.

        Returns
        -------
        bool
            True if the message is still routable.
        """

        if self.ttl > 0:
            self.ttl -= 1

        return self.ttl > 0


    def acknowledge(self) -> None:
        """
        Mark message as acknowledged.
        """

        self.acknowledged = True


    def mark_delivered(self) -> None:
        """
        Mark message as delivered.
        """

        self.delivered = True


    def mark_dropped(self) -> None:
        """
        Mark message as dropped.
        """

        self.dropped = True


    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store deterministic metadata.
        """

        self.metadata[key] = value


    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve metadata.
        """

        return self.metadata.get(
            key,
            default,
        )


    def payload_size(self) -> int:
        """
        Return an approximate payload size.

        This avoids serialization dependencies while providing a
        deterministic metric suitable for routing decisions.
        """

        return len(
            repr(self.payload)
        )


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic snapshot suitable for replay,
        auditing, routing inspection, and debugging.
        """

        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "protocol_version": self.protocol_version,
            "message_type": self.message_type.value,
            "source": self.source,
            "destination": self.destination,
            "sequence": self.sequence,
            "ttl": self.ttl,
            "priority": self.priority,
            "payload": dict(self.payload),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
            "delivered": self.delivered,
            "acknowledged": self.acknowledged,
            "dropped": self.dropped,
        }


    def copy(self) -> "Message":
        """
        Produce a deterministic copy of the message.

        The message identity is preserved because copies represent
        the same logical protocol event.
        """

        return Message(
            message_id=self.message_id,
            correlation_id=self.correlation_id,
            protocol_version=self.protocol_version,
            message_type=self.message_type,
            source=self.source,
            destination=self.destination,
            sequence=self.sequence,
            ttl=self.ttl,
            priority=self.priority,
            payload=dict(self.payload),
            timestamp=self.timestamp,
            metadata=dict(self.metadata),
            delivered=self.delivered,
            acknowledged=self.acknowledged,
            dropped=self.dropped,
        )