from influx.network.sync.sync_session import SyncSession


def test_finish():

    session = SyncSession(
        session_id="s1",
        peer_id="node1",
    )

    session.finish()

    assert session.completed


def test_snapshot():

    session = SyncSession(
        session_id="s1",
        peer_id="node1",
    )

    assert "peer_id" in session.snapshot()