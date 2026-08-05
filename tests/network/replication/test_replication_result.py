from influx.network.replication.replication_result import (
    ReplicationResult,
)


def test_success_result():

    result = ReplicationResult(
        success=True,
        replicas_written=3,
    )

    assert result.success


def test_snapshot():

    result = ReplicationResult(
        success=True,
    )

    assert "success" in result.snapshot()