from influx.network_sync.chain_selector import (
    ChainScore,
    ChainSelector,
)


def test_chain_selection():

    selector = ChainSelector()

    chains = [
        ChainScore(
            height=10,
            root_hash="a",
        ),
        ChainScore(
            height=20,
            root_hash="b",
        ),
    ]

    selected = selector.select(
        chains
    )

    assert selected is not None

    assert (
        selected.height
        == 20
    )


def test_equal_height_determinism():

    selector = ChainSelector()

    chains = [
        ChainScore(
            height=5,
            root_hash="aaa",
        ),
        ChainScore(
            height=5,
            root_hash="bbb",
        ),
    ]

    selected = selector.select(
        chains
    )

    assert selected is not None

    assert (
        selected.root_hash
        == "bbb"
    )


def test_empty_selection():

    selector = ChainSelector()

    assert (
        selector.select([])
        is None
    )