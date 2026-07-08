from typing import List, Dict, Any

from influx.runtime.node import InFluxNode
from influx.config.settings import InFluxConfig


class SimulatedCluster:
    """
    Deterministic multi-node cluster simulation.

    Now executes full InFlux runtime pipeline per node.
    """

    def __init__(self, node_count: int, config: InFluxConfig):
        self.node_count = node_count
        self.config = config

        self.nodes: List[InFluxNode] = [
            InFluxNode(config.__dict__) for _ in range(node_count)
        ]

    def start_all(self) -> None:
        for node in self.nodes:
            node.start()

    def stop_all(self) -> None:
        for node in self.nodes:
            node.stop()

    def broadcast_event(self, event: Dict[str, Any]) -> List[Any]:
        """
        Send identical event to all nodes and execute full pipeline.
        """

        results = []

        for node in self.nodes:
            result = node.process_event(event)
            results.append(result)

        return results

    def verify_determinism(self, results: List[Any]) -> Dict[str, Any]:
        """
        Ensure all nodes produced identical final outputs.
        """

        if not results:
            return {"deterministic": True}

        reference = results[0]

        mismatches = []

        for i, r in enumerate(results[1:], start=1):
            if r["final"] != reference["final"]:
                mismatches.append(i)

        return {
            "deterministic": len(mismatches) == 0,
            "mismatched_nodes": mismatches,
            "reference_hash": reference["final"]["final_hash"] if "final" in reference else None,
        }


def run_full_deterministic_test():
    """
    End-to-end system validation.
    """

    config = InFluxConfig()

    cluster = SimulatedCluster(node_count=3, config=config)

    cluster.start_all()

    event = {
        "type": "SYSTEM_TEST_EVENT",
        "payload": "influx_full_stack_validation"
    }

    results = cluster.broadcast_event(event)

    verification = cluster.verify_determinism(results)

    cluster.stop_all()

    return {
        "event": event,
        "verification": verification,
        "node_outputs": results
    }


if __name__ == "__main__":
    output = run_full_deterministic_test()
    print(output)