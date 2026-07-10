from __future__ import annotations

from abc import ABC, abstractmethod

from influx.network.message import NetworkMessage
from influx.network.peer import Peer


class NetworkTransport(ABC):
    """
    Abstract deterministic transport layer.

    Every transport implementation must inherit from this class.
    """

    @abstractmethod
    def send(self, peer: Peer, message: NetworkMessage) -> None:
        """
        Send a deterministic message to a single peer.
        """
        raise NotImplementedError

    @abstractmethod
    def broadcast(self, message: NetworkMessage) -> None:
        """
        Broadcast a deterministic message to all connected peers.
        """
        raise NotImplementedError

    @abstractmethod
    def receive(self) -> list[NetworkMessage]:
        """
        Receive all pending deterministic messages.
        """
        raise NotImplementedError