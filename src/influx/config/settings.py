from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class EngineConfig:
    """
    Base configuration block for all engines.
    Immutable to guarantee deterministic execution.
    """
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InFluxConfig:
    """
    Global deterministic configuration for the entire system.
    This is the single source of truth for node initialization.
    """

    version: str = "1.4.4"

    consensus: EngineConfig = EngineConfig()
    ledger: EngineConfig = EngineConfig()
    state: EngineConfig = EngineConfig()
    replication: EngineConfig = EngineConfig()
    economic: EngineConfig = EngineConfig()
    network: EngineConfig = EngineConfig()
    storage: EngineConfig = EngineConfig()
    crypto: EngineConfig = EngineConfig()

    debug_mode: bool = False
    strict_determinism: bool = True

    def get_engine_config(self, name: str) -> EngineConfig:
        """
        Deterministic lookup of engine configuration.
        """
        return getattr(self, name)