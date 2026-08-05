from typing import Dict, Any

from influx.consensus.engine import ConsensusEngine
from influx.ledger.engine import LedgerEngine
from influx.state.engine import StateEngine
from influx.replication.engine import ReplicationEngine
from influx.economic.engine import EconomicEngine
from influx.observability.logger import DeterministicLogger


class InFluxNode:
    """
    Deterministic runtime execution node with full observability.

    Every step is now traceable and replayable.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.node_id = config.get("node_id", str(id(self)))
        self.running = False

        self.logger = DeterministicLogger()

        self.consensus = ConsensusEngine(config.get("consensus", {}))
        self.ledger = LedgerEngine(config.get("ledger", {}))
        self.state = StateEngine(config.get("state", {}))
        self.replication = ReplicationEngine(config.get("replication", {}))
        self.economic = EconomicEngine(config.get("economic", {}))

    def initialize(self) -> None:
        self.consensus.initialize()
        self.ledger.initialize()
        self.state.initialize()

        self.logger.log_event("NODE_INIT", {
            "status": "initialized"
        })

    def start(self) -> None:
        self.initialize()
        self.running = True

        self.logger.log_event("NODE_START", {
            "status": "running"
        })

    def stop(self) -> None:
        self.running = False

        self.logger.log_event("NODE_STOP", {
            "status": "stopped"
        })

    # -----------------------------
    # CORE EXECUTION PIPELINE
    # -----------------------------

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:

        self.logger.log_event("EVENT_RECEIVED", event)

        # 1. State transition
        before_state = self.state.get_state()
        new_state = self.state.apply(event)
        after_state = self.state.get_state()

        self.logger.log_state_transition(before_state, after_state)

        # 2. Consensus proposal
        proposal = self.consensus.propose_state(
            new_state,
            validator={
                "id": self.node_id,
                "reputation": 1.0
            },
        )

        # 3. Self-vote (deterministic baseline)
        votes = [proposal]

        # 4. Consensus evaluation
        consensus_result = self.consensus.evaluate_votes(votes)

        self.logger.log_consensus(consensus_result)

        # 5. Finalization
        final = self.consensus.finalize_state(consensus_result)

        # 6. Ledger commit
        ledger_commit = self.ledger.commit(final)

        # 7. Replication
        replication_result = self.replication.broadcast(final)

        self.logger.log_replication(replication_result)

        # 8. Economic layer
        self.economic.apply_event(final)

        return {
            "state": new_state,
            "consensus": consensus_result,
            "final": final,
            "ledger": ledger_commit,
            "trace": self.logger.export()
        }

    def status(self) -> Dict[str, Any]:
        return {
            "running": self.running,
            "engines": {
                "consensus": self.consensus.initialized,
                "ledger": self.ledger.initialized,
                "state": True
            }
        }