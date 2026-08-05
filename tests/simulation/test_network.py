from typing import Any, Dict, List

from influx.runtime.node import InFluxNode
from influx.config.settings import InFluxConfig


class SimulatedTestNetwork:
    """
    Deterministic multi-node simulation network.

    Used to verify:
    - consensus convergence
    - state determinism
    - ledger consistency
    """

    def __init__(self, node_count: int):
        self.node_count = node_count
        self.nodes: List[InFluxNode] = []
        self.results: List[Dict[str, Any]] = []

    def setup(self):
        config = InFluxConfig()

        for _ in range(self.node_count):
            node = InFluxNode(config.__dict__)
            node.start()
            self.nodes.append(node)

    def broadcast_event(self, event: Dict[str, Any]):
        self.results = []

        for node in self.nodes:
            result = node.process_event(event)
            self.results.append(result)

        return self.results

    def verify_determinism(self) -> Dict[str, Any]:
        """
        Ensures all nodes converge to identical final state hash.
        """

        hashes = []

        for r in self.results:
            hashes.append(r["final"]["final_state_hash"])

        unique_hashes = set(hashes)

        return {
            "total_nodes": self.node_count,
            "unique_hashes": len(unique_hashes),
            "deterministic": len(unique_hashes) == 1,
            "hashes": hashes
        }