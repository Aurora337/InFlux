from typing import Any, Dict


class SimulatedCluster:
    """
    Lightweight deterministic cluster simulator.
    """

    def __init__(self, node_count: int, config: Any):
        self.node_count = node_count
        self.config = config
        self.nodes: list[str] = []
        self.results: list[dict[str, Any]] = []

    # -----------------------------
    # START NODES
    # -----------------------------

    def start_all(self):
        self.nodes = ["node_" + str(i) for i in range(self.node_count)]

    # -----------------------------
    # BROADCAST EVENT
    # -----------------------------

    def broadcast_event(self, event: Dict[str, Any]):
        self.results = []

        for node in self.nodes:
            result = {
                "node": node,
                "event": event,
                "state_hash": f"hash_{node}_{event.get('type')}",
            }
            self.results.append(result)

        return self.results

    # -----------------------------
    # DETERMINISM CHECK
    # -----------------------------

    def verify_determinism(self, results=None):
        results = results or self.results

        hashes = [r["state_hash"] for r in results]
        unique_hashes = set(hashes)

        return {
            "nodes": len(results),
            "unique_hashes": len(unique_hashes),
            "deterministic": len(unique_hashes) == 1,
            "hashes": hashes
        }
    
    # -----------------------------
    # STOP NODES
    # -----------------------------

    def stop_all(self) -> None:
        """
        Gracefully stop every simulated node.
        """
        self.nodes.clear()
        self.results.clear()