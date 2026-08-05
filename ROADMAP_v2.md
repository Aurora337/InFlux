# InFlux v5.x Roadmap

Version: v5.0.0 → v5.7.0

---

## Vision

Advance InFlux from completed deterministic infrastructure into integrated protocol economics, where policy modules execute through a single deterministic economic path without introducing non-deterministic side channels.

---

## Baseline Status

### v5.0.0 — Economic Core
✅ **Complete (Implementation)**

- Deterministic Event System
- Economic State / Transition / Snapshot
- Economic Executor (single mutation path)
- Economic Scheduler / Validator / Metrics
- Economic Engine orchestration

---

## v5.0.1 — Protocol Integration

⏳ **In Progress**

This milestone connects every major subsystem through the deterministic event pipeline without introducing any new economic policy modules.

### Integration Flow

Governance → Event Bus → Economic Core → Ledger  
Governance → Event Bus → Economic Core → Consensus  
Contracts → Event Bus → Economic Core  
Economic Core → Runtime Coordinator  
Economic Core → Metrics / Monitoring

### Objectives

- Governance integration
- Smart contract integration
- Runtime coordination
- Metrics integration
- End-to-end deterministic replay validation

### Scope

- Governance event emission integrated with Event Bus
- Contract runtime event emission integrated with Event Bus
- Deterministic projection from events to `EconomicOperation`
- Economic Core outputs integrated with ledger commit path
- Economic Core outputs integrated with consensus-visible state transitions
- Runtime coordinator hooks integrated with Economic Core outcomes
- Metrics pipeline integrated with Economic Core execution lifecycle
- Replay and deterministic integration validation

---

## v5.1.0 — Reward Engine

*Planned*

Policy-only reward module. Introduces reward rules, not new mutation infrastructure.

- Validator reward policy
- Treasury distribution policy
- Contract execution incentive policy
- Reward epoch and release schedule
- Reward operations emitted as `EconomicOperation` objects only

---

## v5.2.0 — Deterministic Fee Market

*Planned*

- Deterministic fee policy and market rules
- Congestion-aware fee calculation (deterministic inputs only)
- Fee burn / redistribution policy via Economic Executor

---

## v5.3.0 — Treasury Execution

*Planned*

- Treasury policy modules integrated with governance outcomes
- Deterministic treasury release mechanics
- Audit-friendly treasury operation trails through Economic Executor

---

## v5.4.0 — Hybrid Reproduction Engine

*Planned*

- Deterministic hybrid reproduction policy framework
- Policy-to-operation compilation into economic execution path
- Replay-safe reproduction invariants

---

## v5.5.0 — Economic Simulation

*Planned*

- Multi-scenario deterministic economic simulations
- Stress and adversarial economic behavior modeling
- Policy tuning under replayable conditions

---

## v5.6.0 — Protocol Invariants

*Planned*

- Formalized economic and governance invariants
- Cross-subsystem deterministic invariant checks
- Invariant regression suite integrated with CI

---

## v5.7.0 — Formal Verification

*Planned*

- Verification targets for critical deterministic economic paths
- Runtime/economic interface proofs (selected properties)
- Verification-guided hardening of consensus-economic interactions

---

## Legacy Runtime Vector Note

The remaining runtime vector failures target a deprecated execution interface that predates the keyword-based `ContractRuntime.execute()` API. These vectors should be migrated to the current deterministic runtime interface. Runtime behavior should not be rolled back to satisfy deprecated interface expectations unless an explicit compatibility layer is intentionally introduced.

---

## Architecture Freeze Note (v5.0 Baseline)

The Event System and Economic Core are stable protocol interfaces. Future milestones should extend these interfaces rather than modify them. New protocol features (Rewards, Fees, Treasury, Hybrid Reproduction) must be implemented as policies that emit `EconomicOperation` objects executed exclusively through the Economic Executor.
