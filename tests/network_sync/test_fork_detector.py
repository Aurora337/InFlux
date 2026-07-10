from influx.network_sync.fork_detector import (
    ForkCandidate,
    ForkDetector,
)


def test_create_candidate():

    candidate = ForkCandidate(
        height=10,
        root_hash="root10",
    )

    assert (
        candidate.height
        == 10
    )

    assert (
        candidate.root_hash
        == "root10"
    )


def test_detect_conflict():

    detector = ForkDetector()

    local = ForkCandidate(
        height=5,
        root_hash="rootA",
    )

    remote = ForkCandidate(
        height=5,
        root_hash="rootB",
    )

    assert detector.compare(
        local,
        remote,
    )


def test_no_conflict():

    detector = ForkDetector()

    local = ForkCandidate(
        height=5,
        root_hash="same",
    )

    remote = ForkCandidate(
        height=5,
        root_hash="same",
    )

    assert (
        detector.compare(
            local,
            remote,
        )
        is False
    )


def test_detect_multiple_candidates():

    detector = ForkDetector()

    candidates = [
        ForkCandidate(
            1,
            "rootA",
        ),
        ForkCandidate(
            1,
            "rootB",
        ),
        ForkCandidate(
            1,
            "rootC",
        ),
    ]

    conflicts = detector.detect(
        candidates
    )

    assert (
        len(conflicts)
        == 2
    )