from influx.observability.tracer import ExecutionTracer
from typing import Any, Dict

from influx.runtime.node import InFluxNode
from influx.config.settings import InFluxConfig

from influx.testing.fault_injector import FaultInjector
from influx.testing.byzantine_adversary import ByzantineAdversary


class FaultTestNetwork:
    """
    Hybrid adversarial simulation network.

    Combines:
    - Random faults (network instability)
    - Byzantine attacks (intentional malicious behavior)
    """

    def __init__(
        self,
        node_count: int,
        corruption_rate: float = 0.0,
        drop_rate: float = 0.0,
        byzantine_rate: float = 0.0
    ):
        self.node_count = node_count
        self.corruption_rate = corruption_rate
        self.drop_rate = drop_rate
        self.byzantine_rate = byzantine_rate

        self.nodes = []
        self.results = []

        self.faults = FaultInjector()
        self.adversary = ByzantineAdversary()

        self.tracer = ExecutionTracer()
    # -----------------------------
    # SETUP NODES
    # -----------------------------

    def setup(self):
        config = InFluxConfig()

        for _ in range(self.node_count):
            node = InFluxNode(config.__dict__)
            node.start()
            self.nodes.append(node)

    # -----------------------------
    # BROADCAST WITH FULL ADVERSARIAL LAYER
    # -----------------------------

    def broadcast_event(self, event: Dict[str, Any]):
        self.results = []

        for node in self.nodes:

            # Step 1: apply random faults
            modified_event = self.faults.apply_faults(
                event,
                corruption_rate=self.corruption_rate,
                drop_rate=self.drop_rate
            )

            if modified_event is None:
                continue

            # Step 2: simulate Byzantine manipulation (state-level attack)
            modified_event = self.adversary.forge_state(
                modified_event,
                aggression=self.byzantine_rate
            )
              # ✅ STEP 3: ADD TRACING HERE (BEFORE EXECUTION)
            self.tracer.trace(
                node_id=str(getattr(node, "id", "node")),
                event_type="event_processed",
                data={
                    "event": modified_event,
                    "node_index": len(self.results)
            }
        )

            result = node.process_event(modified_event)
            self.results.append(result)

        return self.results

    # -----------------------------
    # DETECTION LOGIC
    # -----------------------------

    def verify_determinism(self):
        hashes = []

        for r in self.results:
            hashes.append(r["final"]["final_state_hash"])

        unique_hashes = set(hashes)

        return {
            "nodes_executed": len(self.results),
            "unique_hashes": len(unique_hashes),
            "deterministic": len(unique_hashes) == 1,
            "fault_rate": self.corruption_rate,
            "drop_rate": self.drop_rate,
            "byzantine_rate": self.byzantine_rate,
            "hashes": hashes
        }