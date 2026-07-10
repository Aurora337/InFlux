from __future__ import annotations

from typing import Dict, List, Optional

from .connection import Connection


class ConnectionPool:
    """
    Maintains reusable network connections.

    The pool provides deterministic allocation,
    release, and cleanup behavior.
    """

    def __init__(self) -> None:
        self._connections: Dict[str, Connection] = {}
        self._available: Dict[str, Connection] = {}


    def allocate(self, connection: Connection) -> Connection:
        """
        Add a connection to the pool.
        """

        self._connections[
            connection.connection_id
        ] = connection

        self._available[
            connection.connection_id
        ] = connection

        return connection


    def release(self, connection_id: str) -> None:
        """
        Return a connection to available state.
        """

        connection = self._connections.get(connection_id)

        if connection is None:
            return

        self._available[connection_id] = connection


    def available(self) -> List[Connection]:
        """
        Return currently available connections.
        """

        return list(
            self._available.values()
        )


    def active(self) -> List[Connection]:
        """
        Return active connections.
        """

        return [
            connection
            for connection in self._connections.values()
            if connection.connected
        ]


    def cleanup(self) -> None:
        """
        Remove closed connections.
        """

        remove_ids = [
            connection_id
            for connection_id, connection
            in self._connections.items()
            if not connection.connected
        ]

        for connection_id in remove_ids:
            self._connections.pop(
                connection_id,
                None
            )

            self._available.pop(
                connection_id,
                None
            )


    def lookup(
        self,
        connection_id: str
    ) -> Optional[Connection]:
        """
        Retrieve connection by ID.
        """

        return self._connections.get(
            connection_id
        )


    def snapshot(self) -> dict:
        """
        Deterministic pool snapshot.
        """

        return {
            "total": len(
                self._connections
            ),
            "available": len(
                self._available
            ),
            "active": len(
                self.active()
            ),
        }