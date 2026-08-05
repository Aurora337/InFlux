#!/usr/bin/env python3
"""
Documentation Generator for InFlux.

Generates structured documentation from code and audit artifacts.
"""

import json
import os
from pathlib import Path


class DocumentationGenerator:
    """Generates InFlux documentation from source code and audit reports."""

    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_api_reference(self) -> str:
        """Generate API reference documentation."""
        content = """# InFlux API Reference

## Network Layer

### Transport
- `Transport` — Abstract transport interface
- `TransportSession` — Session management
- `TransportConfig` — Transport configuration
- `TransportType` — MEMORY, TCP, WEBSOCKET

### Routing
- `Router` — Message routing
- `RouteTable` — Route management
- `Route` — Individual route
- `RoutingPolicy` — Policy enforcement

### Gossip
- `Gossip` — Gossip protocol engine
- `GossipMessage` — Message format
- `GossipState` — State management
- `GossipValidator` — Message validation

### Consensus
- `Consensus` — Consensus state machine
- `ConsensusConfig` — Configuration
- `ConsensusResult` — Result tracking
- `ConsensusValidator` — Validation
- `ConsensusMetrics` — Performance metrics

### Replication
- `Replication` — State replication
- `ReplicationConfig` — Configuration
- `ReplicationState` — State tracking
- `ReplicationValidator` — Validation

### Sync
- `Sync` — State synchronization
- `SyncConfig` — Configuration
- `SyncSession` — Session management
- `SyncSnapshot` — State snapshots

### Network
- `NetworkCoordinator` — Coordinator
- `NetworkState` — Global state
- `NetworkMetrics` — Metrics
- `NetworkEvents` — Event handling

## Runtime Layer

### Bootstrap
- `Bootstrap` — Initialization
- `Lifecycle` — Lifecycle management
- `State` — Runtime state
- `Signals` — Signal handling

### Execution
- `Executor` — Task execution
- `Scheduler` — Task scheduling
- `Dispatcher` — Task dispatch
- `Monitor` — Health monitoring

### Services
- `Service` — Service interface
- `Services` — Service registry
- `Coordinator` — Service coordination

## Testnet Layer

### Process Management
- `ProcessManager` — Subprocess management
- `NodeRunner` — Node execution
- `NetworkBootstrapper` — Network formation
- `TestnetOrchestrator` — Full lifecycle

## Harness

### Deterministic Validation
- `DeterministicValidator` — Multi-node validation
- `ConvergenceAssertions` — State convergence
- `NetworkScenarios` — 10/100/1000 node tests
- `FaultScenarios` — Fault tolerance
- `AdversarialScenarios` — Attack simulation

### Economic Stress
- `EconomicStressEngine` — Stress testing
- `EconomicMetrics` — Metric computation
- 8 economic scenarios
"""
        path = self.output_dir / "api" / "index.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)

    def generate_developer_guide(self) -> str:
        """Generate developer documentation."""
        content = """# InFlux Developer Manual

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation
```bash
pip install -e .
```

### Running Tests
```bash
pytest tests/
```

## Architecture

### Network Stack
The network layer provides deterministic communication:
- Transport abstraction (memory, TCP, WebSocket)
- Message routing with policy enforcement
- Gossip protocol for peer-to-peer communication
- Consensus engine for distributed agreement
- State replication and synchronization

### Deterministic Execution
All components follow deterministic patterns:
- Dataclass-based state management
- Snapshot-based state verification
- No non-deterministic operations
- Reproducible test scenarios

### Economic Engine
The economic layer manages:
- Supply and reserve tracking
- Participant and validator management
- Transaction processing
- Economic stress testing

## Development Workflow

1. Clone the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Run full test suite
6. Submit pull request

## Coding Standards

- Type hints required for all functions
- Dataclasses for state objects
- No mutable default arguments
- Comprehensive docstrings
- Test coverage for all new code
"""
        path = self.output_dir / "developer" / "index.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)

    def generate_operator_guide(self) -> str:
        """Generate operator documentation."""
        content = """# InFlux Node Operator Guide

## Running a Testnet

### Single Node
```bash
python -m influx.testnet.node_runner --port 9000
```

### Multi-Node Cluster
```python
from influx.testnet.testnet_orchestrator import TestnetOrchestrator
orchestrator = TestnetOrchestrator(base_port=9000)
result = orchestrator.run_testnet(node_count=4)
```

### Dashboard
```bash
python -m dashboard.app
```
Access at http://localhost:8080

## Monitoring

### Key Metrics
- Validator health
- Consensus rounds
- Gossip propagation
- State synchronization
- Transaction throughput
- Network latency

### Health Checks
- Node connectivity
- State consistency
- Resource usage

## Troubleshooting

### Common Issues
1. Port conflicts — Use unique ports per node
2. Timeout errors — Increase timeout values
3. State divergence — Check network connectivity
"""
        path = self.output_dir / "operator" / "index.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)

    def generate_validator_guide(self) -> str:
        """Generate validator documentation."""
        content = """# InFlux Validator Guide

## Validator Setup

### Requirements
- Stable network connection
- Sufficient computational resources
- Valid node identity

### Configuration
```python
from influx.network.node.node_config import NodeConfig
config = NodeConfig(
    node_id="validator-1",
    port=9000,
)
```

### Lifecycle
1. Initialization
2. Registration
3. Active validation
4. Consensus participation
5. Graceful shutdown

## Consensus Participation

### Rounds
1. Propose
2. Vote
3. Commit
4. Sync

### Validation
- State consistency checks
- Message signature verification
- Economic parameter validation
"""
        path = self.output_dir / "validator" / "index.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)

    def generate_economic_spec(self) -> str:
        """Generate economic specification."""
        return self._write_spec(
            "economic",
            "# InFlux Economic Specification\n\n",
            [
                ("Supply Model", "Deterministic supply with controlled expansion"),
                ("Reserve Mechanism", "Reserve-backed stability with ratio tracking"),
                ("Transaction Processing", "Fee-based transaction model"),
                ("Validator Economics", "Validator incentives and rewards"),
                ("Stress Testing", "8 economic scenarios for resilience testing"),
            ]
        )

    def generate_network_spec(self) -> str:
        """Generate network specification."""
        return self._write_spec(
            "network",
            "# InFlux Network Specification\n\n",
            [
                ("Transport Layer", "Memory, TCP, WebSocket transport"),
                ("Routing", "Policy-based message routing"),
                ("Gossip Protocol", "Epidemic broadcast for peer-to-peer"),
                ("Consensus", "BFT-inspired state machine"),
                ("Replication", "Deterministic state replication"),
                ("Synchronization", "Cross-node state sync"),
            ]
        )

    def _write_spec(self, name: str, header: str, sections: list) -> str:
        content = header
        for title, desc in sections:
            content += f"## {title}\n{desc}\n\n"
        path = self.output_dir / name / "index.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)

    def generate_all(self) -> list[str]:
        """Generate all documentation."""
        generated = []
        generated.append(self.generate_api_reference())
        generated.append(self.generate_developer_guide())
        generated.append(self.generate_operator_guide())
        generated.append(self.generate_validator_guide())
        generated.append(self.generate_economic_spec())
        generated.append(self.generate_network_spec())
        return generated


def main() -> int:
    generator = DocumentationGenerator()
    generated = generator.generate_all()
    print(f"Generated {len(generated)} documentation files:")
    for path in generated:
        print(f"  - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
