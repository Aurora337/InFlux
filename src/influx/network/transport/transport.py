from __future__ import annotations

from abc import ABC, abstractmethod

from .transport_session import TransportSession


class Transport(ABC):
    """
    Abstract transport interface.

    All transport implementations must provide the same
    deterministic behavior regardless of underlying protocol.
    """


    @abstractmethod
    def open(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Open a transport session.
        """

        raise NotImplementedError


    @abstractmethod
    def close(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Close a transport session.
        """

        raise NotImplementedError


    @abstractmethod
    def send(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:
        """
        Send bytes through transport.
        """

        raise NotImplementedError


    @abstractmethod
    def receive(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:
        """
        Receive bytes through transport.
        """

        raise NotImplementedError


    @abstractmethod
    def heartbeat(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Verify transport health.
        """

        raise NotImplementedError