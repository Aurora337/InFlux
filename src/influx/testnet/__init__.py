"""
InFlux Production Testnet Framework.

Provides:

- genesis bootstrap
- node registration
- cluster formation
- synchronization primitives
- network deployment
- validator simulation
- metrics collection
- fault testing
"""

from .bootstrap import (
    bootstrap_from_genesis,
    load_genesis,
)

from .clusters import (
    Cluster,
    ClusterMembership,
    ClusterRegistry,
)

from .registry import (
    NodeRegistry,
)

from .synchronization import (
    ClusterStateExchange,
    SynchronizationResult,
    SynchronizationSession,
)

from .node import (
    TestnetNode,
)

from .network import (
    TestnetNetwork,
)

from .deployment import (
    TestnetDeployment,
)

from .validator import (
    ValidatorManager,
    ValidatorState,
)

from .simulation import (
    TestnetSimulation,
)

from .metrics import (
    NetworkMetrics,
)

from .faults import (
    FaultInjector,
)

from .exceptions import (
    TestnetError,
    NodeError,
    NetworkError,
    SimulationError,
)


__all__ = [
    # Bootstrap
    "bootstrap_from_genesis",
    "load_genesis",

    # Cluster layer
    "Cluster",
    "ClusterMembership",
    "ClusterRegistry",

    # Registry
    "NodeRegistry",

    # Synchronization
    "ClusterStateExchange",
    "SynchronizationResult",
    "SynchronizationSession",

    # Node/network layer
    "TestnetNode",
    "TestnetNetwork",

    # Deployment
    "TestnetDeployment",

    # Validator layer
    "ValidatorManager",
    "ValidatorState",

    # Simulation
    "TestnetSimulation",

    # Metrics
    "NetworkMetrics",

    # Fault testing
    "FaultInjector",

    # Exceptions
    "TestnetError",
    "NodeError",
    "NetworkError",
    "SimulationError",
]