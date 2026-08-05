from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExternalMessage:
    """
    Represents a message from an external system.
    """

    network: str

    payload: dict


class ExternalAdapter:
    """
    Provides controlled external network interaction.
    """

    def __init__(
        self,
    ) -> None:

        self._messages: list[ExternalMessage] = []

    def receive(
        self,
        message: ExternalMessage,
    ) -> None:
        """
        Receive external message.
        """

        self._messages.append(
            message
        )

    def messages(
        self,
    ) -> list[ExternalMessage]:
        """
        Return received messages.
        """

        return list(
            self._messages
        )

    def count(
        self,
    ) -> int:
        """
        Return external message count.
        """

        return len(
            self._messages
        )