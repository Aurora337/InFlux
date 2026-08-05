from influx.network.cluster.cluster_failover import ClusterFailover


def test_trigger():
    failover = ClusterFailover()

    failover.trigger()

    assert failover.active
    assert failover.failovers == 1


def test_recover():
    failover = ClusterFailover()

    failover.trigger()
    failover.recover()

    assert not failover.active