from influx.state_root.merkle_tree import (
    MerkleTree,
)


def test_empty_tree():

    tree = MerkleTree(
        []
    )

    root = tree.build_root()

    assert isinstance(
        root,
        str,
    )

    assert len(root) == 64


def test_single_leaf():

    tree = MerkleTree(
        [
            "alice:100",
        ]
    )

    root = tree.build_root()

    assert isinstance(
        root,
        str,
    )


def test_multiple_leaves():

    tree = MerkleTree(
        [
            "alice:100",
            "bob:50",
            "carol:25",
        ]
    )

    root = tree.build_root()

    assert isinstance(
        root,
        str,
    )

    assert len(root) == 64


def test_deterministic_root():

    first = MerkleTree(
        [
            "alice:100",
            "bob:50",
        ]
    ).build_root()

    second = MerkleTree(
        [
            "alice:100",
            "bob:50",
        ]
    ).build_root()

    assert (
        first
        ==
        second
    )


def test_snapshot():

    tree = MerkleTree(
        [
            "node:1",
        ]
    )

    snapshot = tree.snapshot()

    assert (
        "leaves"
        in snapshot
    )

    assert (
        "root"
        in snapshot
    )