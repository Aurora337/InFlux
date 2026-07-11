from influx.operations.health import HealthStatus
from influx.operations.monitor import OperationsMonitor


def test_monitor_records_health() -> None:
    monitor = OperationsMonitor()

    monitor.record(
        HealthStatus(
            component_id="node-1",
            healthy=True,
        )
    )

    report = monitor.report()

    assert report.healthy_count() == 1
    assert report.unhealthy_count() == 0