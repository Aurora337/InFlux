from influx.network.gossip.gossip_message import (
    GossipMessage,
)

from influx.network.gossip.gossip_table import (
    GossipTable,
)


def create_message(
    message_id=None,
):
    message = GossipMessage(
        origin="node-1",
        payload={
            "event": "test",
        },
    )

    if message_id is not None:
        message.message_id = message_id

    return message


def test_add_message():

    table = GossipTable()

    message = create_message()

    result = table.add(
        message
    )

    assert result
    assert table.count() == 1


def test_duplicate_message():

    table = GossipTable()

    message = create_message()

    table.add(
        message
    )

    result = table.add(
        message
    )

    assert not result


def test_lookup_message():

    table = GossipTable()

    message = create_message()

    table.add(
        message
    )

    found = table.lookup(
        message.message_id
    )

    assert found is message


def test_remove_message():

    table = GossipTable()

    message = create_message()

    table.add(
        message
    )

    result = table.remove(
        message.message_id
    )

    assert result
    assert table.count() == 0


def test_active_messages():

    table = GossipTable()

    active = create_message()

    expired = create_message()

    expired.ttl = 0

    table.add(active)

    table.add(expired)

    messages = table.active_messages()

    assert active in messages
    assert expired not in messages


def test_snapshot():

    table = GossipTable()

    message = create_message()

    table.add(
        message
    )

    snapshot = table.snapshot()

    assert message.message_id in snapshot