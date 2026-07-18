from influx.network.replication.replication import Replication
from influx.network.replication.replication_validator import (
    ReplicationValidator,
)


def test_validate():
    validator = ReplicationValidator()

    assert validator.validate(
        Replication(replication_id="rep-1")
    )