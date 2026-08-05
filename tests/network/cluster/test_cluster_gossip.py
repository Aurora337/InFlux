from influx.network.cluster.cluster_gossip import ClusterGossip


def test_send_receive():
    gossip = ClusterGossip()

    gossip.send()
    gossip.receive()

    assert gossip.messages_sent == 1
    assert gossip.messages_received == 1


def test_snapshot():
    gossip = ClusterGossip()

    assert "messages_sent" in gossip.snapshot()