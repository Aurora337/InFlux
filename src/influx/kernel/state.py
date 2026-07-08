from typing import Any, List, Dict


class State:
    """
    Compatibility state object used by replay,
    consensus, validator, and simulation tests.
    """

    def __init__(self, epoch: int = 0, supply: float = 0.0, participants: int = 0):
        self.epoch = epoch
        self.supply = supply
        self.participants = participants

        self.ledger: List[Any] = []
        self.height: int = 0
        self.state_hash: str = "genesis"

    def apply(self, block: Any = None) -> None:
        if block is not None:
            self.ledger.append(block)
            self.height += 1
            self.state_hash = self.compute_hash()

    def compute_hash(self) -> str:
        return f"hash_{self.epoch}_{self.height}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "supply": self.supply,
            "participants": self.participants,
            "ledger": self.ledger,
            "height": self.height,
            "state_hash": self.state_hash,
        }
    
    
     
     

    