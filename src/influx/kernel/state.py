from typing import Any, List, Dict
from influx.crypto.hash import DeterministicHasher


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

    def apply(self, block) -> None:
        if not self.validate_transition(block):
            raise ValueError("Invalid state transition")

        if any(
            existing.to_dict() == block.to_dict()
            for existing in self.ledger
        ):
            return

        self.ledger.append(block)
        self.height = block.height
        self.state_hash = self.compute_hash()

    def validate_transition(self, block) -> bool:
        if block.height < 0:
            return False

        if not isinstance(block.previous_hash, str):
            return False

        if len(block.previous_hash) != 64:
            return False

        if not isinstance(block.state_hash, str):
            return False

        return True

    def compute_hash(self) -> str:
        return DeterministicHasher.hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "supply": self.supply,
            "participants": self.participants,
            "ledger": self.ledger,
            "height": self.height,
        }
        
    

    
        
    
    
     
     

    