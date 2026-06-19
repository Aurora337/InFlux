from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    epoch: int
    supply: float
    participants: int

    def to_dict(self):
        return {
            "epoch": self.epoch,
            "supply": self.supply,
            "participants": self.participants,
        }
