from typing import Any, Dict, List

from influx.crypto.hash import DeterministicHasher


class LedgerEngine:
    """
    Deterministic append-only ledger.

    This is the immutable truth layer of InFlux.
    Every state transition must be recorded here.
    """

    def __init__(self, config: dict):
        self.config = config
        self.chain: List[Dict[str, Any]] = []
        self.last_hash: str | None = None
        self.initialized = False

    def initialize(self) -> None:
        self.chain = []
        self.last_hash = None
        self.initialized = True

    # -----------------------------
    # CORE LEDGER ENTRY LOGIC
    # -----------------------------

    def commit(self, payload: Any) -> Dict[str, Any]:
        """
        Append-only deterministic commit.
        """

        entry = {
            "index": len(self.chain),
            "payload": payload,
            "previous_hash": self.last_hash,
        }

        entry_hash = DeterministicHasher.hash(entry)
        entry["hash"] = entry_hash

        self.chain.append(entry)
        self.last_hash = entry_hash

        return entry

    # -----------------------------
    # LEDGER VALIDATION
    # -----------------------------

    def verify_chain(self) -> bool:
        """
        Deterministically verify ledger integrity.
        """

        prev_hash = None

        for i, entry in enumerate(self.chain):
            expected_structure = {
                "index": i,
                "payload": entry["payload"],
                "previous_hash": prev_hash,
            }

            computed_hash = DeterministicHasher.hash(expected_structure)

            if computed_hash != entry["hash"]:
                return False

            prev_hash = entry["hash"]

        return True

    # -----------------------------
    # STATE RECONSTRUCTION INPUT
    # -----------------------------

    def get_event_stream(self) -> List[Any]:
        """
        Extract replayable event stream from ledger.
        """

        return [entry["payload"] for entry in self.chain]

    # -----------------------------
    # LEDGER STATE
    # -----------------------------

    def get_state(self) -> Dict[str, Any]:
        return {
            "length": len(self.chain),
            "last_hash": self.last_hash,
            "valid": self.verify_chain()
        }