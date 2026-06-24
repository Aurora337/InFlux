#!/usr/bin/env python3
"""Run deterministic cluster emergence simulation and write artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.kernel.cluster import ClusterThresholds, NodeRole
from influx.kernel.cluster.simulation import ClusterEvent, default_event_stream, run_cluster_emergence_simulation


def _parse_events(path: Path) -> list[ClusterEvent]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("events input must be a JSON array")

    events: list[ClusterEvent] = []
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        vector = entry.get("alignment_vector", [0.9, 0.9, 0.9, 0.9])
        if not isinstance(vector, list) or len(vector) != 4:
            raise ValueError("alignment_vector must be a list of 4 values")

        events.append(
            ClusterEvent(
                event_id=str(entry.get("event_id", "")),
                node_id=str(entry.get("node_id", "")),
                role=NodeRole(str(entry.get("role", "SN"))),
                vpu=float(entry.get("vpu", 0.0)),
                alignment_vector=(float(vector[0]), float(vector[1]), float(vector[2]), float(vector[3])),
                ctor_slot=int(entry.get("ctor_slot", 0)),
                reserve_pressure=float(entry.get("reserve_pressure", 0.0)),
            )
        )
    return events


def _render_markdown(report: dict) -> str:
    lines = [
        "# v1.3.7 Cluster Emergence Simulation",
        "",
        f"- Event Count: {report['event_count']}",
        f"- Window Count: {report['window_count']}",
        f"- Simulation Valid: {report['simulation_valid']}",
        f"- Cluster Type Counts: {report['cluster_type_counts']}",
        f"- Lifecycle Counts: {report['lifecycle_counts']}",
        "",
        "## Window Summary",
        "",
        "| Window | Events | Clusters | Types | Lifecycles |",
        "|---|---:|---:|---|---|",
    ]

    for window in report["windows"]:
        types = sorted({cluster["cluster_type"] for cluster in window["clusters"]})
        lifecycles = sorted({cluster["lifecycle"] for cluster in window["clusters"]})
        lines.append(
            f"| {window['window_index']} | {window['event_count']} | {len(window['clusters'])} | "
            f"{', '.join(types) if types else 'none'} | {', '.join(lifecycles) if lifecycles else 'none'} |"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic cluster emergence simulation")
    parser.add_argument(
        "--events-input",
        default="",
        help="Optional JSON array of events. If omitted, built-in deterministic stream is used.",
    )
    parser.add_argument(
        "--output",
        default="testnet/launch/cluster_emergence_report.json",
        help="JSON output path for simulation report",
    )
    parser.add_argument(
        "--markdown-output",
        default="testnet/launch/cluster_emergence_report.md",
        help="Markdown output path for simulation summary",
    )
    args = parser.parse_args()

    if args.events_input:
        events_path = Path(args.events_input)
        if not events_path.is_absolute():
            events_path = ROOT / events_path
        events = _parse_events(events_path)
    else:
        events = default_event_stream()

    report = run_cluster_emergence_simulation(events=events, thresholds=ClusterThresholds())

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    markdown_path = Path(args.markdown_output)
    if not markdown_path.is_absolute():
        markdown_path = ROOT / markdown_path
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")

    print(f"Simulation windows: {report['window_count']}")
    print(f"Simulation clusters: {sum(len(window['clusters']) for window in report['windows'])}")
    print(f"Simulation valid: {report['simulation_valid']}")
    print(f"JSON report: {output_path}")
    print(f"Markdown report: {markdown_path}")


if __name__ == "__main__":
    main()
