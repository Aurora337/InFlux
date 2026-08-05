from __future__ import annotations

from abc import ABC, abstractmethod

from .transport_session import TransportSession


class Transport(ABC):
    """
    Abstract transport interface.

    Defines the deterministic contract every
    transport implementation must provide.

    Examples:
    - TCP transport
    - QUIC transport
    - WebSocket transport
    - Simulation transport
    """


    @abstractmethod
    def open(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Open transport session.
        """

        ...


    @abstractmethod
    def close(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Close transport session.
        """

        ...


    @abstractmethod
    def send(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:
        """
        Send transport payload.
        """

        ...


    @abstractmethod
    def receive(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Receive transport payload.
        """

        ...


    @abstractmethod
    def heartbeat(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Validate transport health.
        """

        ...