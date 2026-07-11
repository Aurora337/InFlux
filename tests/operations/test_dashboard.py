from influx.operations.alerts import AlertManager
from influx.operations.dashboard import OperationsDashboard
from influx.operations.health import (
    HealthReport,
    HealthStatus,
)
from influx.operations.metrics import OperationsMetrics


def test_dashboard_snapshot() -> None:
    dashboard = OperationsDashboard()

    report = HealthReport(
        statuses=[
            HealthStatus(
                component_id="node-1",
                healthy=True,
            ),
        ]
    )

    metrics = OperationsMetrics()
    metrics.nodes_online = 1
    metrics.validators_active = 1

    alerts = AlertManager()

    snapshot = dashboard.snapshot(
        report,
        metrics,
        alerts,
    )

    assert snapshot.health.is_healthy() is True
    assert snapshot.metrics["nodes_online"] == 1
    assert snapshot.alert_count == 0