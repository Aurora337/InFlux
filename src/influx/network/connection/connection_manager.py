from __future__ import annotations

from typing import Dict, Optional

from .connection import Connection
from .connection_metrics import ConnectionMetrics
from .connection_policy import ConnectionPolicy
from .connection_pool import ConnectionPool
from .connection_validator import ConnectionValidator


class ConnectionManager:
    """
    Controls lifecycle of all network connections.
    """

    def __init__(
        self,
        policy: Optional[ConnectionPolicy] = None,
    ) -> None:

        self.pool = ConnectionPool()

        self.metrics = ConnectionMetrics()

        self.policy = (
            policy
            if policy is not None
            else ConnectionPolicy()
        )

        self.validator = ConnectionValidator(
            self.policy
        )

        self.connections: Dict[str, Connection] = {}


    def open(
        self,
        connection: Connection,
    ) -> bool:
        """
        Open a new connection.
        """

        if not self.validator.validate_connection(
            connection.peer,
            list(self.connections.values())
        ):
            self.metrics.record_failure()
            return False


        connection.connect()

        self.connections[
            connection.connection_id
        ] = connection

        self.pool.allocate(
            connection
        )

        self.metrics.record_open()

        return True


    def close(
        self,
        connection_id: str,
    ) -> bool:
        """
        Close an active connection.
        """

        connection = self.connections.get(
            connection_id
        )

        if connection is None:
            return False


        connection.disconnect()

        self.metrics.record_close()

        return True


    def reconnect(
        self,
        connection_id: str,
    ) -> bool:
        """
        Reconnect an existing connection.
        """

        connection = self.connections.get(
            connection_id
        )

        if connection is None:
            return False


        connection.connect()

        self.metrics.record_reconnect()

        return True


    def lookup(
        self,
        connection_id: str,
    ) -> Optional[Connection]:
        """
        Find connection by ID.
        """

        return self.connections.get(
            connection_id
        )


    def broadcast(
        self,
        data: bytes,
    ) -> int:
        """
        Send data to every active connection.

        Returns:
            Number of successful sends.
        """

        sent = 0

        for connection in self.connections.values():

            if connection.connected:

                connection.send(
                    data
                )

                self.metrics.record_sent(
                    len(data)
                )

                sent += 1


        return sent


    def heartbeat_all(self) -> int:
        """
        Send heartbeat to all connections.
        """

        successful = 0

        for connection in self.connections.values():

            if connection.heartbeat():

                successful += 1

            else:

                self.metrics.record_heartbeat_failure()


        return successful


    def snapshot(self) -> dict:
        """
        Return deterministic manager state.
        """

        return {
            "connections": {
                connection_id:
                connection.snapshot()

                for connection_id, connection
                in self.connections.items()
            },
            "metrics": self.metrics.snapshot(),
            "pool": self.pool.snapshot(),
        }