from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque

from .transport_config import TransportConfig
from .transport_session import TransportSession
from .transport_type import TransportType


class Transport:
    """
    Abstract transport interface.

    Provides an in-memory deterministic transport and
    the contract used by specialized implementations.

    Examples:
    - TCP transport
    - QUIC transport
    - WebSocket transport
    - Simulation transport
    """


    def __init__(
        self,
        transport_id: str = "transport",
        transport_type: TransportType = TransportType.MEMORY,
        config: TransportConfig | None = None,
    ) -> None:
        self.transport_id = transport_id
        self.transport_type = transport_type
        self.config = config or TransportConfig(host="127.0.0.1", port=0)
        self._sessions: dict[str, TransportSession] = {}
        self._pending: dict[str, Deque[bytes]] = defaultdict(deque)

    @property
    def active(self) -> bool:
        """Whether at least one transport session is open."""

        return any(session.connected for session in self._sessions.values())

    def open(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Open transport session.
        """

        session.open()
        self._sessions[session.session_id] = session
        return True


    def close(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Close transport session.
        """

        session.close()
        self._sessions.pop(session.session_id, None)
        self._pending.pop(session.session_id, None)
        return True


    def send(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:
        """
        Send transport payload.
        """

        if not self.active or not session.connected:
            return False

        session.record_send(len(data))
        self._pending[session.session_id].append(bytes(data))
        return True


    def receive(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Receive transport payload.
        """

        if not self.active or not session.connected:
            return False

        pending = self._pending[session.session_id]
        if not pending:
            return False

        session.record_receive(len(pending.popleft()))
        return True


    def heartbeat(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Validate transport health.
        """

        return self.active and session.connected
