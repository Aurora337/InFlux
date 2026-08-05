#!/usr/bin/env python3
"""Validate deterministic cluster emergence simulation artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.kernel.cluster.validation import validate_cluster_emergence_report


def _render_markdown(result: dict) -> str:
    lines = [
        "# v1.3.7 Cluster Emergence Validation",
        "",
        f"- report_valid: {result['report_valid']}",
        f"- checks_passed: {result['checks_passed']}/{result['checks_total']}",
        f"- checks_failed: {result['checks_failed']}",
        "",
        "## Failed Checks",
        "",
    ]

    if result["failed_checks"]:
        for check in result["failed_checks"]:
            lines.append(f"- {check}")
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate deterministic cluster emergence report")
    parser.add_argument(
        "--input",
        default="testnet/launch/cluster_emergence_report.json",
        help="Path to simulation report JSON",
    )
    parser.add_argument(
        "--output",
        default="testnet/launch/cluster_emergence_validation.json",
        help="Path to write validation JSON",
    )
    parser.add_argument(
        "--markdown-output",
        default="testnet/launch/cluster_emergence_validation.md",
        help="Path to write validation markdown",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path

    report = json.loads(input_path.read_text(encoding="utf-8"))
    result = validate_cluster_emergence_report(report)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    markdown_path = Path(args.markdown_output)
    if not markdown_path.is_absolute():
        markdown_path = ROOT / markdown_path
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(result), encoding="utf-8")

    print(f"Report valid: {result['report_valid']}")
    print(f"Checks passed: {result['checks_passed']}/{result['checks_total']}")
    print(f"JSON report: {output_path}")
    print(f"Markdown report: {markdown_path}")
    return 0 if result["report_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
