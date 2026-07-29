"""Public protocol for network coordination implementations."""

from __future__ import annotations

from typing import Protocol

from influx.network.message import NetworkMessage


class Coordinator(Protocol):
    """Contract implemented by network coordinators."""

    def connect_peer(self, peer_id: str) -> bool: ...

    def disconnect_peer(self, peer_id: str) -> bool: ...

    def route_message(self, message: NetworkMessage) -> bool: ...

    def synchronize(self) -> bool: ...

    def replicate(self) -> bool: ...

    def snapshot(self) -> dict[str, object]: ...
