from __future__ import annotations

from dataclasses import dataclass
import json

from .exceptions import (
    MessageValidationError,
)


@dataclass(frozen=True, slots=True)
class TransportMessage:
    """
    Represents a deterministic network message.

    Messages contain:

    - protocol version
    - message type
    - sender identifier
    - payload
    """

    version: str

    message_type: str

    sender: str

    payload: dict[str, object]

    def validate(
        self,
    ) -> None:
        """
        Validate message fields.
        """

        if not self.version:

            raise MessageValidationError(
                "missing protocol version"
            )

        if not self.message_type:

            raise MessageValidationError(
                "missing message type"
            )

        if not self.sender:

            raise MessageValidationError(
                "missing sender"
            )

    def serialize(
        self,
    ) -> bytes:
        """
        Serialize message deterministically.
        """

        self.validate()

        encoded = json.dumps(
            {
                "version": self.version,
                "message_type": self.message_type,
                "sender": self.sender,
                "payload": self.payload,
            },
            sort_keys=True,
        )

        return encoded.encode(
            "utf-8"
        )

    @classmethod
    def deserialize(
        cls,
        data: bytes,
    ) -> "TransportMessage":
        """
        Deserialize message bytes.
        """

        try:

            decoded = json.loads(
                data.decode(
                    "utf-8"
                )
            )

        except Exception as exc:

            raise MessageValidationError(
                "invalid message encoding"
            ) from exc

        message = cls(
            version=decoded["version"],
            message_type=decoded["message_type"],
            sender=decoded["sender"],
            payload=decoded["payload"],
        )

        message.validate()

        return message