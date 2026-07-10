from __future__ import annotations

from influx.network.peer import Peer
from influx.network.session import NetworkSession


class SessionManager:
    """
    Manages deterministic peer sessions.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, NetworkSession] = {}

    def open(self, peer: Peer) -> NetworkSession:
        session = NetworkSession(peer)
        session.connect()
        self._sessions[peer.node_id] = session
        return session

    def close(self, node_id: str) -> None:
        session = self._sessions.get(node_id)

        if session is not None:
            session.disconnect()

    def get(self, node_id: str) -> NetworkSession | None:
        return self._sessions.get(node_id)

    def sessions(self) -> list[NetworkSession]:
        return sorted(
            self._sessions.values(),
            key=lambda session: session.peer.node_id,
        )