from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NetworkMessage:
    """
    Represents a cross-network message.
    """

    message_id: str

    source: str

    destination: str

    payload: dict


class MessageRouter:
    """
    Routes interoperability messages.
    """

    def __init__(
        self,
    ) -> None:

        self._messages: list[NetworkMessage] = []

    def send(
        self,
        message: NetworkMessage,
    ) -> None:
        """
        Store outgoing message.
        """

        self._messages.append(
            message
        )

    def messages(
        self,
    ) -> list[NetworkMessage]:
        """
        Return routed messages.
        """

        return list(
            self._messages
        )

    def count(
        self,
    ) -> int:
        """
        Return message count.
        """

        return len(
            self._messages
        )