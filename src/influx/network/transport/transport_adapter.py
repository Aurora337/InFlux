from __future__ import annotations

from dataclasses import dataclass

from .transport import Transport
from .transport_session import TransportSession


@dataclass(slots=True)
class TransportAdapter:
    """
    Adapter wrapper around a transport implementation.

    Allows future protocol implementations to be swapped
    without modifying the network stack.
    """

    transport: Transport


    def open(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Open transport session.
        """

        return self.transport.open(
            session
        )


    def close(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Close transport session.
        """

        return self.transport.close(
            session
        )


    def send(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:
        """
        Send data.
        """

        return self.transport.send(
            session,
            data,
        )


    def receive(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:
        """
        Receive data.
        """

        return self.transport.receive(
            session,
            data,
        )


    def heartbeat(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Execute heartbeat.
        """

        return self.transport.heartbeat(
            session
        )