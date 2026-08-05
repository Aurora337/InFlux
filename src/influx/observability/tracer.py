from typing import Any, Dict, List
import time


class ExecutionTracer:
    """
    Deterministic execution tracing system.

    Captures:
    - node execution events
    - state transitions
    - consensus decisions
    - timing + divergence points
    """

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    # -----------------------------
    # TRACE EVENT
    # -----------------------------

    def trace(self, node_id: str, event_type: str, data: Dict[str, Any]) -> None:
        self.events.append({
            "timestamp": time.time(),
            "node_id": node_id,
            "event_type": event_type,
            "data": data
        })

    # -----------------------------
    # CONSENSUS DIVERGENCE DETECTION
    # -----------------------------

    def detect_divergence(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        hashes: dict[str, int] = {}

        for r in results:
            h = r["final"]["final_state_hash"]
            hashes.setdefault(h, 0)
            hashes[h] += 1

        return {
            "unique_states": len(hashes),
            "distribution": hashes,
            "divergent": len(hashes) > 1
        }

    # -----------------------------
    # STATE COMPARISON ACROSS NODES
    # -----------------------------

    def compare_states(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        states = [r["final"] for r in results]

        reference = states[0] if states else None

        mismatches = []

        for i, state in enumerate(states):
            if state != reference:
                mismatches.append({
                    "node_index": i,
                    "diff": state
                })

        return {
            "total_nodes": len(states),
            "reference_exists": reference is not None,
            "mismatch_count": len(mismatches),
            "mismatches": mismatches
        }

    # -----------------------------
    # FULL REPORT GENERATION
    # -----------------------------

    def generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "divergence": self.detect_divergence(results),
            "state_comparison": self.compare_states(results),
            "trace_events": self.events
        }