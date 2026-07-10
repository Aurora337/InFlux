from influx.network_sync.fork_resolver import (
    ForkResolver,
    ResolvedFork,
)


def test_resolve_single_candidate():

    resolver = ForkResolver()

    result = resolver.resolve(
        [
            (10, "root10"),
        ]
    )

    assert isinstance(
        result,
        ResolvedFork,
    )

    assert result is not None
    assert result.height == 10
    assert result.selected_root == "root10"


def test_resolve_highest_height():

    resolver = ForkResolver()

    result = resolver.resolve(
        [
            (5, "root5"),
            (8, "root8"),
            (3, "root3"),
        ]
    )

    assert result is not None
    assert result.height == 8
    assert result.selected_root == "root8"


def test_resolve_equal_height():

    resolver = ForkResolver()

    result = resolver.resolve(
        [
            (10, "aaa"),
            (10, "zzz"),
        ]
    )

    assert result is not None
    assert result.height == 10
    assert result.selected_root == "zzz"


def test_resolve_empty():

    resolver = ForkResolver()

    assert resolver.resolve([]) is None