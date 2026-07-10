from influx.network.transport.transport import Transport
from influx.network.transport.transport_session import TransportSession


class MockTransport(Transport):
    """
    Simple transport implementation for testing.
    """

    def open(
        self,
        session: TransportSession,
    ) -> bool:

        session.open()

        return True


    def close(
        self,
        session: TransportSession,
    ) -> bool:

        session.close()

        return True


    def send(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:

        session.record_send(
            len(data)
        )

        return True


    def receive(
        self,
        session: TransportSession,
        data: bytes,
    ) -> bool:

        session.record_receive(
            len(data)
        )

        return True


    def heartbeat(
        self,
        session: TransportSession,
    ) -> bool:

        return session.connected