from influx.operations.telemetry import (
    TelemetryCollector,
    TelemetryEvent,
)


def test_record_event() -> None:
    collector = TelemetryCollector()

    collector.record(
        TelemetryEvent(
            event_type="heartbeat",
            source_id="node-1",
            payload={"height": 42},
        )
    )

    assert collector.count() == 1


def test_filter_by_type() -> None:
    collector = TelemetryCollector()

    collector.record(
        TelemetryEvent(
            event_type="heartbeat",
            source_id="node-1",
            payload={},
        )
    )

    collector.record(
        TelemetryEvent(
            event_type="sync",
            source_id="node-2",
            payload={},
        )
    )

    assert len(
        collector.events_by_type("heartbeat")
    ) == 1