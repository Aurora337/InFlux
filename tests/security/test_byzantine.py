from influx.security.byzantine_detector import (
    ByzantineDetector,
    ByzantineEvent,
)


def test_byzantine_detection():

    detector = ByzantineDetector()

    event = detector.detect(
        validator_id="node-1",
        conflicting_votes=3,
    )

    assert isinstance(
        event,
        ByzantineEvent,
    )

    assert event is not None

    assert (
        event.validator_id
        == "node-1"
    )

    assert (
        event.reason
        == "conflicting_votes"
    )


def test_no_byzantine_event():

    detector = ByzantineDetector()

    event = detector.detect(
        validator_id="node-1",
        conflicting_votes=1,
    )

    assert (
        event
        is None
    )


def test_custom_threshold():

    detector = ByzantineDetector()

    event = detector.detect(
        validator_id="node-1",
        conflicting_votes=5,
        threshold=5,
    )

    assert event is not None

    assert (
        event.severity
        == 5
    )