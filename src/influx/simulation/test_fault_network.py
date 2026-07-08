from typing import Any, Dict

from influx.runtime.node import InFluxNode
from influx.config.settings import InFluxConfig

from influx.testing.fault_injector import FaultInjector
from influx.testing.byzantine_adversary import ByzantineAdversary


class FaultTestNetwork:
    def __init__(self, node_count: int, corruption_rate: float = 0.0,
                 drop_rate: float = 0.0, byzantine_rate: float = 0.0):

        self.node_count = node_count
        self.corruption_rate = corruption_rate
        self.drop_rate = drop_rate
        self.byzantine_rate = byzantine_rate

        self.nodes: list[InFluxNode] = []
        self.results: list[dict[str, Any]] = []

        self.faults = FaultInjector()
        self.adversary = ByzantineAdversary()

    def setup(self):
        config = InFluxConfig()

        for _ in range(self.node_count):
            node = InFluxNode(config.__dict__)
            node.start()
            self.nodes.append(node)

    def broadcast_event(self, event: Dict[str, Any]):
        self.results = []

        for node in self.nodes:

            modified_event = self.faults.apply_faults(
                event,
                corruption_rate=self.corruption_rate,
                drop_rate=self.drop_rate
            )

            if modified_event is None:
                continue

            modified_event = self.adversary.forge_state(
                modified_event,
                aggression=self.byzantine_rate
            )

            result = node.process_event(modified_event)
            self.results.append(result)

        return self.results

    def verify_determinism(self):
        hashes = [r["final"]["final_state_hash"] for r in self.results]

        unique_hashes = set(hashes)

        return {
            "nodes_executed": len(self.results),
            "unique_hashes": len(unique_hashes),
            "deterministic": len(unique_hashes) == 1,
            "hashes": hashes
        }