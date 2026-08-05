from __future__ import annotations

from influx.network.session_manager import SessionManager


class NetworkSynchronizer:
    """
    Coordinates deterministic synchronization.
    """

    def __init__(self, sessions: SessionManager):
        self.sessions = sessions

    def synchronize(self) -> int:
        """
        Synchronize every active session.

        Returns the number of synchronized sessions.
        """

        return len(self.sessions.sessions())