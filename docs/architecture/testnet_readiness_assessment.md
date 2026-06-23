# InFlux Testnet Readiness Assessment (v1.3.1)

## Objective

Determine what is required to launch a real multi-node testnet from current repository state.

## Current Capability Snapshot

### Available Now

- Testnet directory scaffolding for bootstrap/config/genesis/state/peers/validators.
- Deterministic report-generation workflows under scripts/testnet and testnet/launch outputs.
- Simulation and verification tooling for consensus/replay/sync-oriented checks.

### Not Yet Sufficient for Real Testnet Launch

- Persistent validator process lifecycle orchestration.
- Network transport and peer discovery protocol implementation.
- Node admission/removal and synchronization controls in live runtime.
- Operational runbooks bound to live node telemetry rather than offline artifacts.

## Readiness Score

Overall real multi-node testnet readiness: 4/10

## Domain Breakdown

| Domain | Ready? | Score (/10) | Notes |
|---|---|---:|---|
| Genesis and config scaffolding | Yes | 7 | Structure exists and can seed deterministic workflows |
| Validator runtime lifecycle | Partial | 3 | Role files exist but lifecycle controls are incomplete |
| Peer discovery and networking | No | 2 | Simulator-based mesh present; production network stack missing |
| Consensus runtime | Partial | 4 | Simulation evidence exists; production network consensus not complete |
| State replication and recovery | Partial | 4 | Deterministic verification scripts exist; runtime replication service incomplete |
| Ledger durability and replay integration | Partial | 5 | Block store and replay tooling exist; full production durability model needs hardening |
| Observability and operational controls | Partial | 4 | Many reports exist; fewer live runtime telemetry pathways |
| Governance gate integration | Yes | 9 | Governance control plane can gate releases when protocol evidence is available |

## Required to Launch Real Multi-Node Testnet

### Must-Have (Blockers)

1. Implement real validator node runtime and process orchestration.
2. Implement peer networking layer with discovery, handshakes, and message transport.
3. Implement consensus service for live validator rounds and fault handling.
4. Implement state replication/recovery paths for lagging/rejoining validators.
5. Define deterministic bootstrap flow from genesis to steady-state network.

### Should-Have (Stability)

1. Integrate ledger persistence/replay with crash recovery checks.
2. Add structured runtime telemetry and health endpoints for nodes.
3. Build repeatable environment scripts for local and CI multi-node bring-up.
4. Add failure-injection scenarios against live network runtime.

### Governance Coupling (Release Control)

1. Feed live testnet outcomes into governance artifacts used by autonomous release governance.
2. Add a release gate requiring successful multi-node testnet evidence for protocol releases.
3. Keep governance score deterministic and artifact-complete before promotion.

## Recommended v1.3.x Sequence

1. v1.3.2: Validator/runtime and network transport baseline.
2. v1.3.3: Consensus and replication service hardening.
3. v1.3.4: Executable testnet orchestration + CI integration.
4. v1.3.5: Governance-coupled protocol release gate using live testnet evidence.

## Conclusion

InFlux is not yet ready for a real multi-node production-like testnet launch, but it has sufficient scaffolding and governance controls to move quickly once runtime protocol gaps are addressed.
