"""report_generator.py

Report generator placeholder: produce text/JSON reports from metrics and test outcomes.
"""

from typing import Dict, Any
import json

class ReportGenerator:
    def __init__(self):
        pass

    def generate_text(self, metrics: Dict[str, Any]) -> str:
        lines = ["In~Flux Test Report", "===================="]
        counters = metrics.get("counters", {})
        gauges = metrics.get("gauges", {})
        lines.append("
Counters:")
        for k, v in counters.items():
            lines.append(f"- {k}: {v}")
        lines.append("
Gauges:")
        for k, v in gauges.items():
            lines.append(f"- {k}: {v}")
        return "\n".join(lines)

    def generate_json(self, metrics: Dict[str, Any]) -> str:
        return json.dumps(metrics, indent=2)

__all__ = ["ReportGenerator"]