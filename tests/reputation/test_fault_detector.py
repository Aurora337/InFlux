from influx.reputation.fault_detector import (
    FaultDetector,
    FaultEvent,
)


def test_fault_detection():

    detector = FaultDetector()

    event = detector.detect(
        validator_id="node-1",
        failures=5,
    )

    assert isinstance(
        event,
        FaultEvent,
    )

    assert event is not None

    assert (
        event.validator_id
        == "node-1"
    )


def test_no_fault():

    detector = FaultDetector()

    event = detector.detect(
        validator_id="node-1",
        failures=1,
    )

    assert (
        event
        is None
    )


def test_custom_threshold():

    detector = FaultDetector()

    event = detector.detect(
        validator_id="node-1",
        failures=2,
        threshold=2,
    )

    assert event is not None