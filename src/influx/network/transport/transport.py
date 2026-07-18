from __future__ import annotations

from dataclasses import dataclass, field

from influx.network.message import NetworkMessage

from .transport_config import TransportConfig
from .transport_session import TransportSession
from .transport_type import TransportType


@dataclass(slots=True)
class Transport:
    """
    Deterministic transport engine.
    """

    transport_id: str
    transport_type: TransportType
    config: TransportConfig

    active: bool = False

    _messages: list[NetworkMessage] = field(
        default_factory=list
    )


    def open(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Open transport session.
        """

        self.config.validate()

        self.active = True

        return True


    def close(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Close transport session.
        """

        self.active = False

        return True


    def send(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:
        """
        Send raw transport bytes.
        """

        if not self.active:
            return False

        self._messages.append(
            NetworkMessage(
                message_id="transport",
                message_type="RAW",
                sender_id=session.session_id,
                receiver_id="",
                epoch=0,
                slot=0,
                timestamp=0,
                payload={
                    "data": data.hex()
                },
            )
        )

        return True


    def receive(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Check if transport has received data.
        """

        if not self.active:
            return False

        return bool(self._messages)

    def heartbeat(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Validate transport liveness.
        """

        return self.active


    def is_open(self) -> bool:
        """
        Return transport state.
        """

        return self.active