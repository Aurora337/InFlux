"""Generate a consolidated v0.6 economic verification PDF audit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.legends import Legend


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports" / "economic"
AUDITS_DIR = ROOT / "docs" / "audits"


@dataclass
class ScenarioSlice:
    label: str
    scenario_name: str
    payload: dict


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def downsample(points: list[tuple[float, float]], max_points: int = 180) -> list[tuple[float, float]]:
    if len(points) <= max_points:
        return points
    stride = max(1, len(points) // max_points)
    sampled = points[::stride]
    if sampled[-1] != points[-1]:
        sampled.append(points[-1])
    return sampled


def series_from_timeseries(payload: dict, key: str) -> list[tuple[float, float]]:
    rows = payload.get("timeseries", [])
    points = [(float(item["epoch"]), float(item[key])) for item in rows]
    return downsample(points)


def parse_markdown_metric(path: Path, pattern: str, default: str = "N/A") -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return default
    return match.group(1).strip()


def max_epoch_growth_rate(payload: dict) -> float:
    rows = payload.get("timeseries", [])
    if len(rows) < 2:
        return 0.0
    max_rate = 0.0
    prev_supply = float(rows[0]["supply"])
    for row in rows[1:]:
        supply = float(row["supply"])
        if prev_supply > 0:
            rate = (supply - prev_supply) / prev_supply
            if rate > max_rate:
                max_rate = rate
        prev_supply = supply
    return max_rate


def reproduction_stats(payload: dict) -> tuple[float, float]:
    rows = payload.get("timeseries", [])
    if not rows:
        return 0.0, 0.0
    values = [float(row.get("reproduction_applied", 0.0)) for row in rows]
    avg_size = sum(values) / len(values)
    max_size = max(values)
    return avg_size, max_size


def build_line_chart(
    title: str,
    x_label: str,
    y_label: str,
    series: list[tuple[str, list[tuple[float, float]], colors.Color]],
    width: float = 6.5 * inch,
    height: float = 3.0 * inch,
) -> KeepTogether:
    drawing = Drawing(width, height)
    plot = LinePlot()
    plot.x = 45
    plot.y = 40
    plot.width = width - 120
    plot.height = height - 80
    plot.lines.strokeWidth = 1.6
    plot.joinedLines = 1

    data = [points for _, points, _ in series]
    plot.data = data

    x_values = [x for _, points, _ in series for (x, _) in points]
    y_values = [y for _, points, _ in series for (_, y) in points]

    plot.xValueAxis.valueMin = min(x_values)
    plot.xValueAxis.valueMax = max(x_values)
    plot.xValueAxis.valueStep = max(1, int((plot.xValueAxis.valueMax - plot.xValueAxis.valueMin) / 5))

    ymin = min(y_values)
    ymax = max(y_values)
    if ymax == ymin:
        ymax = ymin + 1.0
    padding = (ymax - ymin) * 0.08
    plot.yValueAxis.valueMin = ymin - padding
    plot.yValueAxis.valueMax = ymax + padding
    plot.yValueAxis.valueStep = max((plot.yValueAxis.valueMax - plot.yValueAxis.valueMin) / 5, 0.0001)

    for idx, (_, _, color) in enumerate(series):
        plot.lines[idx].strokeColor = color

    legend = Legend()
    legend.x = width - 60
    legend.y = height - 60
    legend.colorNamePairs = [(series[i][2], series[i][0]) for i in range(len(series))]

    drawing.add(plot)
    drawing.add(legend)

    styles = getSampleStyleSheet()
    subtitle = Paragraph(
        f"<b>{title}</b><br/><font size=9>{x_label} | {y_label}</font>",
        styles["Heading4"],
    )
    return KeepTogether([subtitle, Spacer(1, 0.08 * inch), drawing, Spacer(1, 0.2 * inch)])


def main() -> None:
    metrics = load_json(REPORTS_DIR / "metrics.json")

    one_year = ScenarioSlice("1-Year", "steady_growth", load_json(REPORTS_DIR / "1_year_report.json"))
    five_year = ScenarioSlice("5-Year", "five_year_growth", load_json(REPORTS_DIR / "5_year_report.json"))
    ten_year = ScenarioSlice("10-Year", "ten_year_stress", load_json(REPORTS_DIR / "10_year_report.json"))
    horizon = next(
        item for item in metrics["results"] if item["scenario"] == "long_horizon_growth"
    )

    replay_audit = AUDITS_DIR / "v0.2-replay-audit.md"
    consensus_audit = AUDITS_DIR / "v0.3-consensus-audit.md"
    resilience_audit = AUDITS_DIR / "v0.4-resilience-audit.md"
    cross_env_audit = AUDITS_DIR / "v0.5-cross-platform-audit.md"

    replay_determinism = parse_markdown_metric(replay_audit, r"Determinism Score:\s*([0-9.]+)")
    consensus_rate = parse_markdown_metric(consensus_audit, r"Consensus Agreement Rate:\s*([0-9.]+)")
    resilience_recovery = parse_markdown_metric(resilience_audit, r"Recovery Rate:\s*([0-9.]+)")
    cross_env_pass = parse_markdown_metric(cross_env_audit, r"Cross-platform determinism:\s*([A-Z]+)")

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(AUDITS_DIR / "v0.6-economic-verification.pdf"),
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="InFlux v0.6 Economic Verification Audit",
        author="InFlux",
    )

    story = []
    story.append(Paragraph("InFlux v0.6 Economic Verification (Consolidated)", styles["Title"]))
    story.append(Paragraph("Date: 2026-06-19", styles["Normal"]))
    story.append(Paragraph("Evidence source: reports/economic + docs/audits/v0.2-v0.5", styles["Normal"]))
    story.append(Spacer(1, 0.18 * inch))

    story.append(Paragraph("Scenario Summary", styles["Heading2"]))
    scenario_table = Table(
        [
            ["Metric", "Value"],
            ["Scenarios", f"{metrics['scenarios_checked']}"],
            ["Blocks Simulated", f"{metrics['blocks_simulated']:,}"],
            ["Years Simulated", f"{metrics['years_simulated']}"],
            ["Reserve Utilization", f"{metrics['reserve_utilization']}"],
            ["Supply Growth Rate", f"{metrics['supply_growth_rate']}"],
            ["Ledger Integrity", metrics["ledger_integrity"]],
        ],
        colWidths=[2.4 * inch, 3.8 * inch],
    )
    scenario_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.append(scenario_table)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Supply Stability", styles["Heading2"]))
    stability_rows = [["Scenario", "Initial", "Final", "Avg Growth", "Max Epoch Growth"]]
    for section in [one_year, five_year, ten_year]:
        max_growth = max_epoch_growth_rate(section.payload)
        stability_rows.append(
            [
                section.label,
                f"{section.payload['beginning_supply']:.4f}",
                f"{section.payload['ending_supply']:.4f}",
                f"{section.payload['supply_growth_rate']:.6f}",
                f"{max_growth:.6f}",
            ]
        )
    stability_table = Table(stability_rows, colWidths=[1.1 * inch, 1.1 * inch, 1.2 * inch, 1.3 * inch, 1.6 * inch])
    stability_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(stability_table)
    story.append(Spacer(1, 0.12 * inch))

    supply_chart = build_line_chart(
        title="Supply Curves",
        x_label="Epoch",
        y_label="Supply",
        series=[
            (one_year.label, series_from_timeseries(one_year.payload, "supply"), colors.HexColor("#2563eb")),
            (five_year.label, series_from_timeseries(five_year.payload, "supply"), colors.HexColor("#059669")),
            (ten_year.label, series_from_timeseries(ten_year.payload, "supply"), colors.HexColor("#dc2626")),
        ],
    )
    story.append(supply_chart)

    story.append(Paragraph("Reserve Health", styles["Heading2"]))
    reserve_rows = [["Scenario", "Ending Reserve", "Reserve Utilization", "Coverage Ratio (End)"]]
    coverage_series = []
    for section, color in [
        (one_year, colors.HexColor("#2563eb")),
        (five_year, colors.HexColor("#059669")),
        (ten_year, colors.HexColor("#dc2626")),
    ]:
        coverage_ratio = section.payload["ending_reserve"] / max(section.payload["ending_supply"], 1e-9)
        reserve_rows.append(
            [
                section.label,
                f"{section.payload['ending_reserve']:.6f}",
                f"{section.payload['reserve_utilization']:.6f}",
                f"{coverage_ratio:.6f}",
            ]
        )
        coverage_points = [
            (float(row["epoch"]), float(row["reserve_balance"]) / max(float(row["supply"]), 1e-9))
            for row in section.payload.get("timeseries", [])
        ]
        coverage_series.append((section.label, downsample(coverage_points), color))

    reserve_table = Table(reserve_rows, colWidths=[1.1 * inch, 1.6 * inch, 1.6 * inch, 1.8 * inch])
    reserve_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(reserve_table)
    story.append(Spacer(1, 0.12 * inch))
    story.append(
        build_line_chart(
            title="Reserve Coverage Curves (Reserve / Supply)",
            x_label="Epoch",
            y_label="Coverage Ratio",
            series=coverage_series,
        )
    )

    story.append(Paragraph("Participant Dynamics", styles["Heading2"]))
    participant_rows = [["Scenario", "Initial", "Final", "Growth", "Retention"]]
    participation_series = []
    for section, color in [
        (one_year, colors.HexColor("#2563eb")),
        (five_year, colors.HexColor("#059669")),
        (ten_year, colors.HexColor("#dc2626")),
    ]:
        initial = max(int(section.payload["beginning_participants"]), 1)
        final = int(section.payload["ending_participants"])
        growth = (final - initial) / initial
        retention = final / initial
        participant_rows.append([section.label, str(initial), str(final), f"{growth:.6f}", f"{retention:.6f}"])
        participation_points = [
            (float(row["epoch"]), float(row["participants"])) for row in section.payload.get("timeseries", [])
        ]
        participation_series.append((section.label, downsample(participation_points), color))

    participant_table = Table(participant_rows, colWidths=[1.1 * inch, 1.1 * inch, 1.1 * inch, 1.3 * inch, 1.3 * inch])
    participant_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(participant_table)
    story.append(Spacer(1, 0.12 * inch))
    story.append(
        build_line_chart(
            title="Participation Curves",
            x_label="Epoch",
            y_label="Participants",
            series=participation_series,
        )
    )

    story.append(Paragraph("Reproduction Statistics", styles["Heading2"]))
    repro_rows = [["Scenario", "Events", "Average Size", "Maximum Size"]]
    for section in [one_year, five_year, ten_year]:
        avg_size, max_size = reproduction_stats(section.payload)
        repro_rows.append(
            [
                section.label,
                str(section.payload["reproduction_events"]),
                f"{avg_size:.8f}",
                f"{max_size:.8f}",
            ]
        )
    repro_table = Table(repro_rows, colWidths=[1.1 * inch, 1.1 * inch, 1.6 * inch, 1.6 * inch])
    repro_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(repro_table)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Determinism and Consensus Metrics", styles["Heading2"]))
    evidence_table = Table(
        [
            ["Evidence", "Value"],
            ["Replay Determinism Score (v0.2)", replay_determinism],
            ["Consensus Agreement Rate (v0.3)", consensus_rate],
            ["Resilience Recovery Rate (v0.4)", resilience_recovery],
            ["Cross-Environment Determinism (v0.5)", cross_env_pass],
            ["100k Final Hash", horizon["final_state_hash"]],
        ],
        colWidths=[2.9 * inch, 3.3 * inch],
    )
    evidence_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.append(evidence_table)
    story.append(Spacer(1, 0.18 * inch))

    story.append(Paragraph("Observed Strengths", styles["Heading3"]))
    strengths = [
        "Reserve no longer exhausts in the tuned 5-year and 10-year scenarios.",
        "Suite-scale execution remains deterministic with ledger integrity PASS.",
        "Long-horizon (100k block) run remains reproducible with stable reference hash.",
        "Cross-phase evidence remains aligned: replay, consensus, resilience, and economic outputs.",
    ]
    for item in strengths:
        story.append(Paragraph(f"- {item}", styles["Normal"]))

    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Observed Risks", styles["Heading3"]))
    risks = [
        "1-year alias scenario still exhausts reserve under current steady_growth parameters.",
        "Supply growth acceleration in tuned long horizons should be bounded by policy targets before v0.7.",
        "Consensus and replay metrics are imported from prior audits; reruns should be included in release CI.",
    ]
    for item in risks:
        story.append(Paragraph(f"- {item}", styles["Normal"]))

    doc.build(story)
    print(f"Generated: {AUDITS_DIR / 'v0.6-economic-verification.pdf'}")


if __name__ == "__main__":
    main()
