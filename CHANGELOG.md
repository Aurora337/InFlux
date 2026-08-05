# Changelog

All notable changes to the InFlux protocol will be documented in this file.

This project follows a milestone-based development model.

---

# v1.5.0-rc1 — Protocol Validation & Production Readiness (Current)

## Overview

This release candidate marks the transition from feature development to system
maturation. No new protocol features are added. Instead, this milestone proves
that InFlux behaves correctly under realistic and adversarial conditions through
deterministic validation, economic stress testing, process-based testnet
execution, security auditing, and documentation locking.

## Added

### Phase 1 — Release Candidate
* Version bumped to 1.5.0-rc1
* Release branch created for stability-focused development

### Phase 2 — Deterministic Validation Suite
* `harness/deterministic/` — Core deterministic validator engine
  * `deterministic_validator.py` — Runs N nodes and asserts convergence
  * `scenarios/network_scenarios.py` — 10, 100, 1000 node scenarios
  * `scenarios/fault_scenarios.py` — Leader failures, partitions, reconnection
  * `scenarios/adversarial_scenarios.py` — Reordering, duplication, latency
  * `assertions/convergence_assertions.py` — Ledger hash, state root, economic state
* `tests/deterministic/` — Deterministic validation test suite (6 test files)

### Phase 3 — Economic Stress Tests
* `harness/economic-stress/` — Economic stress test engine
  * `economic_stress_engine.py` — Scenario orchestrator
  * 8 economic stress scenarios (whale accumulation, panic selling, dead network,
    explosive adoption, slow adoption, spam attacks, validator dropout,
    exchange outage)
  * `metrics/economic_metrics.py` — Reserve stability, reproduction rate,
    supply expansion, propagation speed, price stability, deterministic convergence

### Phase 4 — Process-Based Testnet
* `src/influx/testnet/process_manager.py` — Launch and manage real node processes
* `src/influx/testnet/node_runner.py` — Run a single node as a subprocess
* `src/influx/testnet/network_bootstrap.py` — Bootstrap N real nodes
* `src/influx/testnet/testnet_orchestrator.py` — Multi-node testnet lifecycle
* Process-based testnet tests (3 test files)

### Phase 5 — Live Network Dashboard
* `dashboard/` — Live network console application
* FastAPI backend with real-time WebSocket metrics
* Displays: cluster topology, validator health, gossip propagation,
  consensus rounds, synchronization, state roots, TPS, latency, memory

### Phase 6 — Security Audit
* `scripts/audit/security/` — Security audit scripts
  * Static analysis, fuzz testing, replay attack testing
  * Invalid state transition testing, economic exploit testing
* `tests/security/` — Security test suite (5 test files)

### Phase 7 — Whitepaper Alignment Audit
* `scripts/audit/whitepaper_alignment/` — Specification alignment audit
  * Alignment auditor, specification tracker, coverage report generator

### Phase 8 — Documentation Lock
* `scripts/generate_docs.py` — Auto-documentation generator from code
* API Reference, Developer Manual, Node Operator Guide, Validator Guide
* Economic Specification, Network Specification, Deployment Guide, CLI Reference

### Phase 9 — v2 Roadmap
* `ROADMAP_v2.md` — v2 planning document
* Smart contract, cross-chain, governance, wallet, explorer, SDK planning

## Improved

* Protocol stability through comprehensive deterministic validation
* Economic resilience through 8 adversarial economic scenarios
* Production readiness through process-based testnet infrastructure
* Security posture through dedicated security audit suite
* Documentation accuracy through whitepaper alignment audit
* Developer experience through auto-generated documentation
---

# v1.4.6 — Import Repair & Module Consolidation

## Fixed

* Repaired 5 source files with broken imports referencing removed modules:
  - `src/influx/network/manager.py` - Replaced `influx.transport.deterministic_transport` with `influx.network.transport.transport`, replaced `influx.network.discovery.discovery` with `influx.network.discovery.discovery_manager`, replaced `influx.network.synchronization.synchronization` with `influx.network.sync.sync`
  - `src/influx/network/network_coordinator.py` - Replaced `influx.network.synchronization.synchronization` with `influx.network.sync.sync`
  - `src/influx/network/coordinator.py` - Replaced `influx.network.routing.message` with `influx.network.message`
  - `src/influx/network/__init__.py` - Updated all broken imports to point to correct package locations
  - `src/influx/network/errors.py` - Added missing `PeerNotFound`, `SessionClosed`, `SerializationError` exception classes

* `src/influx/testnet/network.py` - Added missing `__test__ = False` attribute to `TestnetNetwork` dataclass to eliminate 3 `PytestCollectionWarning` warnings

## Improved

* Test suite passes: **1528 tests, 0 failures, 0 warnings** (full suite)
* All imports now point to canonical package locations
* Cleaner `__init__.py` with only valid exports
* Zero pytest warnings across the entire test suite

---

# v1.4.5 — Codebase Completion & Consolidation

## Fixed

* Moved 5 misplaced test files from `src/` to `tests/` (wrong locations fixed)
* Removed 4 duplicate standalone module files superseded by package equivalents:
  - `src/influx/network/connection.py` (package already existed)
  - `src/influx/network/discovery.py` (package already existed)
  - `src/influx/network/sync.py` (package already existed)
  - `src/influx/network/transport.py` (package already existed with `NetworkTransport` alias)
* Removed duplicate `src/influx/transport/` package (superseded by `src/influx/network/transport/`)
* Fixed 2 tests that referenced incorrect `ClusterState` API

## Improved

* Test suite passes: **1528 tests, 0 failures** (previously 1524)
* Cleaner module structure with single canonical implementations
* All imports updated to point to package equivalents

## Added

* New derived tests for `ClusterState` enum values
* TODO.md completion tracking

---

# v1.4.4 — Documentation Normalization

## Added

* Documentation index
* Protocol specification library
* Contributor guide
* Code of Conduct
* Security Policy
* Documentation structure normalization

## Improved

* Repository organization
* Documentation consistency
* Specification cross-references

---

# v1.4.3 — Economic Propagation Validation

## Added

* Economic propagation validation
* Cluster propagation testing
* Economic propagation audit

---

# v1.4.2 — Cross-Cluster Synchronization

## Added

* Cross-cluster synchronization framework
* Synchronization validation
* Cluster communication improvements

---

# v1.4.1 — Multi-Cluster Testnet Formation

## Added

* Multi-cluster formation
* Cluster discovery
* Cluster lifecycle validation

---

# v1.4.0 — Prototype Testnet Bring-Up

## Added

* Prototype testnet framework
* Initial validator deployment
* Testnet readiness improvements

---

# Earlier Releases

Previous milestones include:

* v1.3.x Testnet Readiness
* v1.2.x Governance Baseline
* v1.1.x Synchronization Audit
* v1.0.x Core Protocol Foundation

Refer to the `docs/releases/` directory for detailed release notes.
