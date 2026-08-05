from influx.operations.health import (
    HealthReport,
    HealthStatus,
)


def test_health_status() -> None:
    status = HealthStatus(
        component_id="node-1",
        healthy=True,
        message="ok",
    )

    assert status.component_id == "node-1"
    assert status.healthy is True
    assert status.message == "ok"


def test_health_report() -> None:
    report = HealthReport(
        statuses=[
            HealthStatus("a", True),
            HealthStatus("b", False),
            HealthStatus("c", True),
        ]
    )

    assert report.healthy_count() == 2
    assert report.unhealthy_count() == 1
    assert report.is_healthy() is False