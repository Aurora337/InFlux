from influx.network.cluster.cluster_recovery import ClusterRecovery


def test_complete():
    recovery = ClusterRecovery()

    recovery.complete()

    assert recovery.recovered
    assert recovery.recoveries == 1


def test_reset():
    recovery = ClusterRecovery()

    recovery.complete()
    recovery.reset()

    assert not recovery.recovered