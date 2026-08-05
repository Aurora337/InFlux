from __future__ import annotations

from dataclasses import dataclass, field

from .sync_config import SyncConfig
from .sync_session import SyncSession
from .sync_state import SyncState


@dataclass(slots=True)
class Sync:
    """
    Deterministic synchronization task.
    """

    sync_id: str

    config: SyncConfig = field(
        default_factory=SyncConfig
    )

    state: SyncState = SyncState.INITIALIZING

    sessions: list[SyncSession] = field(
        default_factory=list
    )

    def connect(
        self,
    ) -> bool:
        """
        Begin peer connection.
        """

        self.state = SyncState.CONNECTING
        return True

    def synchronize(
        self,
    ) -> bool:
        """
        Begin synchronization.
        """

        self.state = SyncState.SYNCHRONIZING
        return True

    def complete(
        self,
    ) -> bool:
        """
        Finish synchronization.
        """

        self.state = SyncState.SYNCHRONIZED
        return True

    def fail(
        self,
    ) -> bool:
        """
        Fail synchronization.
        """

        self.state = SyncState.FAILED
        return True

    def add_session(
        self,
        session: SyncSession,
    ) -> bool:
        """
        Register a synchronization session.
        """

        self.sessions.append(session)
        return True

    def session_count(
        self,
    ) -> int:
        """
        Return active session count.
        """

        return len(self.sessions)