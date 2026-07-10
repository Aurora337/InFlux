from __future__ import annotations

from typing import Dict, Optional

from .transport import Transport
from .transport_adapter import TransportAdapter
from .transport_metrics import TransportMetrics
from .transport_session import TransportSession


class TransportManager:
    """
    Controls active transport sessions.

    The manager coordinates transport lifecycle while
    keeping transport implementations isolated behind
    the Transport abstraction.
    """

    def __init__(
        self,
        transport: Transport,
    ) -> None:

        self.adapter = TransportAdapter(
            transport
        )

        self.metrics = TransportMetrics()

        self.sessions: Dict[
            str,
            TransportSession
        ] = {}


    def open(
        self,
        session: TransportSession,
    ) -> bool:
        """
        Open a transport session.
        """

        success = self.adapter.open(
            session
        )

        if not success:
            self.metrics.record_failure()

            return False


        self.sessions[
            session.session_id
        ] = session

        self.metrics.record_open()

        return True


    def close(
        self,
        session_id: str,
    ) -> bool:
        """
        Close a transport session.
        """

        session = self.sessions.get(
            session_id
        )

        if session is None:
            return False


        success = self.adapter.close(
            session
        )

        if success:
            self.metrics.record_close()

        return success


    def send(
        self,
        session_id: str,
        data: bytes,
    ) -> bool:
        """
        Send bytes through a session.
        """

        session = self.sessions.get(
            session_id
        )

        if session is None:
            return False


        success = self.adapter.send(
            session,
            data,
        )

        if success:
            self.metrics.record_send(
                len(data)
            )

        else:
            self.metrics.record_failure()


        return success


    def receive(
        self,
        session_id: str,
        data: bytes,
    ) -> bool:
        """
        Receive bytes through a session.
        """

        session = self.sessions.get(
            session_id
        )

        if session is None:
            return False


        success = self.adapter.receive(
            session,
            data,
        )

        if success:
            self.metrics.record_receive(
                len(data)
            )

        else:
            self.metrics.record_failure()


        return success


    def heartbeat_all(self) -> int:
        """
        Verify all sessions.
        """

        healthy = 0

        for session in self.sessions.values():

            if self.adapter.heartbeat(
                session
            ):
                healthy += 1

            else:
                self.metrics.record_heartbeat_failure()


        return healthy


    def lookup(
        self,
        session_id: str,
    ) -> Optional[TransportSession]:
        """
        Retrieve a session.
        """

        return self.sessions.get(
            session_id
        )


    def snapshot(self) -> dict:
        """
        Deterministic manager snapshot.
        """

        return {
            "sessions": {
                session_id:
                    session.snapshot()

                for session_id, session
                in self.sessions.items()
            },

            "metrics":
                self.metrics.snapshot(),
        }