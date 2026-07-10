from __future__ import annotations

from typing import Dict

from .replication_session import ReplicationSession
from .replication_state import ReplicationState


class ReplicationManager:
    """
    Tracks deterministic replication sessions.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, ReplicationSession] = {}

    def create(
        self,
        session: ReplicationSession,
    ) -> bool:
        """
        Register a replication session.
        """

        if session.session_id in self._sessions:
            return False

        self._sessions[session.session_id] = session
        return True

    def lookup(
        self,
        session_id: str,
    ) -> ReplicationSession | None:
        """
        Lookup a replication session.
        """

        return self._sessions.get(session_id)

    def remove(
        self,
        session_id: str,
    ) -> bool:
        """
        Remove a session.
        """

        if session_id not in self._sessions:
            return False

        del self._sessions[session_id]
        return True

    def active(
        self,
    ) -> list[ReplicationSession]:
        """
        Return active sessions.
        """

        return [
            session
            for session in self._sessions.values()
            if session.state
            in (
                ReplicationState.CREATED,
                ReplicationState.SYNCING,
                ReplicationState.VERIFYING,
            )
        ]

    def completed(
        self,
    ) -> list[ReplicationSession]:
        """
        Return completed sessions.
        """

        return [
            session
            for session in self._sessions.values()
            if session.state
            in (
                ReplicationState.COMMITTED,
                ReplicationState.FAILED,
                ReplicationState.CANCELLED,
            )
        ]

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic manager snapshot.
        """

        return {
            session_id: self._sessions[
                session_id
            ].snapshot()
            for session_id
            in sorted(self._sessions)
        }