from influx.history.history_index import (
    HistoryIndex,
    HistoryIndexEntry,
)


def test_add_index():

    index = HistoryIndex()

    entry = index.add(
        1,
        "root1",
    )

    assert isinstance(
        entry,
        HistoryIndexEntry,
    )

    assert (
        entry.height
        == 1
    )


def test_get_index():

    index = HistoryIndex()

    index.add(
        5,
        "root5",
    )

    result = index.get(
        5
    )

    assert result is not None

    assert (
        result.root_hash
        == "root5"
    )


def test_contains():

    index = HistoryIndex()

    index.add(
        2,
        "root2",
    )

    assert index.contains(
        2
    )

    assert (
        index.contains(
            99
        )
        is False
    )


def test_index_ordering():

    index = HistoryIndex()

    index.add(
        5,
        "a",
    )

    index.add(
        1,
        "b",
    )

    index.add(
        3,
        "c",
    )

    assert (
        index.heights()
        ==
        [1, 3, 5]
    )