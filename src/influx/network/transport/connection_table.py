from __future__ import annotations

from .connection import Connection
from .connection_state import ConnectionState


class ConnectionTable:
    """
    Deterministic registry of active network connections.
    """

    def __init__(self) -> None:
        self._connections: dict[str, Connection] = {}

    def add(
        self,
        connection: Connection,
    ) -> bool:
        """
        Register a connection.
        """

        if connection.connection_id in self._connections:
            return False

        self._connections[
            connection.connection_id
        ] = connection

        return True

    def remove(
        self,
        connection_id: str,
    ) -> bool:
        """
        Remove a connection.
        """

        if connection_id not in self._connections:
            return False

        del self._connections[
            connection_id
        ]

        return True

    def lookup(
        self,
        connection_id: str,
    ) -> Connection | None:
        """
        Lookup a connection.
        """

        return self._connections.get(
            connection_id
        )

    def active_connections(
        self,
    ) -> list[Connection]:
        """
        Return connected peers.
        """

        return [
            connection
            for connection in self._connections.values()
            if connection.state == ConnectionState.CONNECTED
        ]

    def count(
        self,
    ) -> int:
        """
        Number of registered connections.
        """

        return len(self._connections)

    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic snapshot.
        """

        return {
            connection_id: connection.snapshot()
            for connection_id, connection
            in self._connections.items()
        }