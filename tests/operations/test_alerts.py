from influx.operations.alerts import (
    Alert,
    AlertManager,
    AlertSeverity,
)


def test_add_alert() -> None:
    manager = AlertManager()

    manager.add(
        Alert(
            component_id="node-1",
            severity=AlertSeverity.WARNING,
            message="High latency",
        )
    )

    assert manager.count() == 1


def test_filter_by_severity() -> None:
    manager = AlertManager()

    manager.add(
        Alert(
            component_id="node-1",
            severity=AlertSeverity.INFO,
            message="Started",
        )
    )

    manager.add(
        Alert(
            component_id="node-2",
            severity=AlertSeverity.CRITICAL,
            message="Offline",
        )
    )

    critical = manager.by_severity(AlertSeverity.CRITICAL)

    assert len(critical) == 1
    assert critical[0].component_id == "node-2"