"""
InFlux v5.0.1
Deterministic Runtime Pipeline

The pipeline defines the canonical execution order
for protocol state transitions.
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Any


class PipelineStage(str, Enum):
    """
    Canonical protocol execution stages.
    """

    WALLET = "wallet"

    RPC = "rpc"

    CONTRACT = "contract"

    EVENT = "event"

    ECONOMIC = "economic"

    LEDGER = "ledger"

    CONSENSUS = "consensus"

    NETWORK = "network"

    FINALIZED = "finalized"



@dataclass
class PipelineContext:
    """
    Shared deterministic execution context.
    """

    execution_id: str

    block_height: int = 0

    state_root: str | None = None

    metadata: dict[str, Any] | None = None



class RuntimePipeline:
    """
    Coordinates deterministic protocol execution.
    """

    def __init__(self):

        self.stages = [
            PipelineStage.WALLET,
            PipelineStage.RPC,
            PipelineStage.CONTRACT,
            PipelineStage.EVENT,
            PipelineStage.ECONOMIC,
            PipelineStage.LEDGER,
            PipelineStage.CONSENSUS,
            PipelineStage.NETWORK,
            PipelineStage.FINALIZED,
        ]


    def get_stages(self) -> list[PipelineStage]:
        """
        Return canonical execution order.
        """

        return list(self.stages)


    def validate_stage(
        self,
        stage: PipelineStage,
    ) -> bool:
        """
        Verify stage exists.
        """

        return stage in self.stages