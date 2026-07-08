"""Generate economic stress test reports."""


class StressReport:
    def __init__(self, metrics_list: list):
        self.metrics_list = metrics_list

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = ["ECONOMIC STRESS TEST REPORT", "=" * 50]

        for metrics in self.metrics_list:
            lines.append("")
            lines.append(f"Timeframe: {metrics.timeframe_name} ({metrics.timeframe_days} days)")
            lines.append(f"  Epochs: {metrics.epochs_run}")
            lines.append(f"  Initial Supply: {metrics.initial_supply:.2f}")
            lines.append(f"  Final Supply: {metrics.final_supply:.2f}")
            lines.append(f"  Supply Growth: {metrics.supply_growth_percent:.4f}%")
            lines.append(f"  Validators: {metrics.final_validators}")
            lines.append(f"  Participation: {metrics.final_participation_percent:.2f}%")
            lines.append(f"  Reserve Balance: {metrics.reserve_balance:.2f}")

        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)

    def csv_export(self) -> str:
        """Export metrics as CSV."""
        lines = [
            "Timeframe,Days,Epochs,InitialSupply,FinalSupply,SupplyGrowth%,Validators,Participation%,ReserveBalance"
        ]

        for metrics in self.metrics_list:
            line = (
                f"{metrics.timeframe_name},"
                f"{metrics.timeframe_days},"
                f"{metrics.epochs_run},"
                f"{metrics.initial_supply:.2f},"
                f"{metrics.final_supply:.2f},"
                f"{metrics.supply_growth_percent:.4f},"
                f"{metrics.final_validators},"
                f"{metrics.final_participation_percent:.2f},"
                f"{metrics.reserve_balance:.2f}"
            )
            lines.append(line)

        return "\n".join(lines)


class ReportGenerator:
    def __init__(self):
        pass

    def generate(self, metrics_list: list) -> StressReport:
        """Generate a stress test report from metrics."""
        return StressReport(metrics_list)


__all__ = ["StressReport", "ReportGenerator"]
