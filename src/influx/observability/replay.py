from typing import Any, Dict


class ReplayEngine:
    """
    Deterministic replay system for InFlux execution traces.

    Converts raw execution logs into a step-by-step timeline.
    """

    def __init__(self, trace_report: Dict[str, Any]):
        self.trace_report = trace_report

    # -----------------------------
    # BASIC TIMELINE VIEW
    # -----------------------------

    def render_timeline(self) -> None:
        events = self.trace_report.get("trace_events", [])

        print("\n=== INFLUX EXECUTION TIMELINE ===\n")

        for i, event in enumerate(events):
            print(f"[{i}] Node: {event['node_id']}")
            print(f"    Type: {event['event_type']}")
            print(f"    Data: {event['data']}")
            print(f"    Time: {event['timestamp']}")
            print("")

    # -----------------------------
    # DIVERGENCE ANALYSIS
    # -----------------------------

    def render_divergence(self) -> None:
        divergence = self.trace_report.get("divergence", {})

        print("\n=== CONSENSUS DIVERGENCE REPORT ===\n")
        print(f"Unique States: {divergence.get('unique_states')}")
        print(f"Divergent: {divergence.get('divergent')}")
        print(f"Distribution: {divergence.get('distribution')}\n")

    # -----------------------------
    # STATE MISMATCH REPORT
    # -----------------------------

    def render_state_mismatches(self) -> None:
        comparison = self.trace_report.get("state_comparison", {})

        print("\n=== STATE COMPARISON REPORT ===\n")
        print(f"Total Nodes: {comparison.get('total_nodes')}")
        print(f"Mismatches: {comparison.get('mismatch_count')}\n")

        for m in comparison.get("mismatches", []):
            print(f"Node {m['node_index']} diverged:")
            print(m["diff"])
            print("")