# Repository Hygiene Audit

- Date: 2026-06-23
- Branch: v1.1.1-sync-ops-audit
- Source command: git status --short --untracked-files=all
- Note: This report excludes its own path from the analyzed inventory.

## Classification Legend

- SAFE_TO_KEEP: Expected and acceptable to keep tracked in repo.
- SAFE_TO_DELETE: Disposable artifact or accidental file that can be removed.
- NEEDS_REVIEW: Potentially legitimate but risky or unclear; requires maintainer decision.
- SHOULD_BE_GITIGNORED: Build/runtime-generated artifact that should be excluded by .gitignore.

## Inventory Summary

- Total changed paths: 192
- Modified: 55
- Deleted: 62
- Untracked: 75

## Findings

| Path | Git Status | Classification | Rationale |
|---|---|---|---|
| docs/audit/release_integrity_report.json |  M | SAFE_TO_KEEP | Expected generated-and-committed audit artifact for release gating. |
| docs/audit/repository_health.json |  M | SAFE_TO_KEEP | Expected generated-and-committed audit artifact for release gating. |
| harness/economic-stress/__pycache__/economic_verification_engine.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/economic-stress/__pycache__/metrics_collector.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/economic-stress/__pycache__/simulation_runner.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/economic-stress/__pycache__/stress_report.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/economic-stress/economic_verification_engine.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| harness/economic-stress/simulation_runner.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| harness/node-mesh-sim/__pycache__/consensus_simulator.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/node-mesh-sim/__pycache__/fault_injection_harness.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/node-mesh-sim/consensus_simulator.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| harness/node-mesh-sim/fault_injection_harness.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| harness/replay-engine/__pycache__/environment_report.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/replay-engine/__pycache__/replay_audit.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/replay-engine/__pycache__/replay_report.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/replay-engine/__pycache__/replay_runner.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/replay-engine/__pycache__/replay_scenario_runner.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/replay-engine/__pycache__/replay_store.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| harness/replay-engine/environment_report.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| harness/replay-engine/replay_audit.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| harness/replay-engine/replay_runner.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| harness/replay-engine/replay_scenario_runner.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| multi_node_consensus.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| replay_audit.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| scripts/audit/__pycache__/release_integrity_audit.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| scripts/audit/__pycache__/repository_health_dashboard.cpython-314.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| scripts/generate_demo_ledger.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| src/kernel/README.md |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/__pycache__/runtime.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/__pycache__/state.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/alignment/README.md |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/alignment/classifier.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/alignment/router.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/alignment/tags.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/alignment/validator.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/economic/README.md |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/economic/__pycache__/delta_c.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/economic/__pycache__/reproduction.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/economic/constants.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/economic/delta_c.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/economic/reproduction.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/economic/state_machine.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/ledger/README.md |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/ledger/__pycache__/block.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/ledger/__pycache__/block_store.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/ledger/__pycache__/hash_sync.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/ledger/__pycache__/pipeline.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/ledger/__pycache__/serialization.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/ledger/block.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/ledger/block_store.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/ledger/ctor_sort.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/ledger/hash_sync.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/ledger/pipeline.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/ledger/serialization.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/math/README.md |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/math/dro.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/math/fpe.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/math/sgf.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/README.md |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/__pycache__/vn.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/node/an.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/fi_node.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/ln.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/ptn.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/ren.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/sn.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/node/vn.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/runtime.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/state.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/sync/README.md |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/sync/__pycache__/shcm.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/sync/ainf.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/sync/gde.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/sync/ros.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/sync/shcm.py |  D | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| tests/audit/__pycache__/test_release_integrity.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/audit/__pycache__/test_repository_health_dashboard.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_consensus.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_consensus_failure.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_cross_env_reports.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_cross_env_reports.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_economic_stress.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_economic_stress.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_economic_verification.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_economic_verification.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_fault_injection.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_fault_injection.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_multi_node_consensus.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_multi_node_consensus.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_network_simulation_integration.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_network_simulation_integration.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_persistent_ledger.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_persistent_ledger.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_replay_audit.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_replay_audit.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_replay_scenarios.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_replay_scenarios.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_replay_verification.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_replay_verification.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_validator_consensus_agreement.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_validator_consensus_agreement.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_validator_consensus_mismatch.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_validator_consensus_mismatch.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_validator_hash_agreement.cpython-314-pytest-9.1.1.pyc |  M | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/__pycache__/test_validator_hash_agreement.cpython-314.pyc |  D | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| tests/golden/test_consensus.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_consensus_failure.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_economic_stress.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_multi_node_consensus.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_network_simulation_integration.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_persistent_ledger.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_replay_audit.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_replay_verification.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_validator_consensus_agreement.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_validator_consensus_mismatch.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| tests/golden/test_validator_hash_agreement.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| verify_ledger.py |  M | NEEDS_REVIEW | Source/test code changed; requires functional review. |
| ........................................................ | ?? | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. |
| .vscode/.easycpp | ?? | SAFE_TO_DELETE | Editor-local artifact not required for project source control. |
| 56 | ?? | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. |
| PS | ?? | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. |
| To | ?? | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. |
| __pycache__/compare_env_reports.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| bash | ?? | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. |
| package-lock.json | ?? | NEEDS_REVIEW | Node lockfile in primarily Python repo; keep only if Node toolchain is intentional. |
| pyproject.toml | ?? | SAFE_TO_KEEP | Project configuration file; expected in source control. |
| python | ?? | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. |
| scripts/dev.sh | ?? | NEEDS_REVIEW | New helper script; verify ownership, usage, and security before keeping. |
| src/influx.egg-info/PKG-INFO | ?? | SHOULD_BE_GITIGNORED | Packaging metadata generated by build/install. |
| src/influx.egg-info/SOURCES.txt | ?? | SHOULD_BE_GITIGNORED | Packaging metadata generated by build/install. |
| src/influx.egg-info/dependency_links.txt | ?? | SHOULD_BE_GITIGNORED | Packaging metadata generated by build/install. |
| src/influx.egg-info/entry_points.txt | ?? | SHOULD_BE_GITIGNORED | Packaging metadata generated by build/install. |
| src/influx.egg-info/top_level.txt | ?? | SHOULD_BE_GITIGNORED | Packaging metadata generated by build/install. |
| src/influx/__init__.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/__pycache__/__init__.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/__pycache__/cli.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/cli.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/README.md | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/__init__.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/__pycache__/__init__.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/__pycache__/runtime.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/__pycache__/state.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/alignment/README.md | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/alignment/classifier.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/alignment/router.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/alignment/tags.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/alignment/validator.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/economic/README.md | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/economic/__pycache__/delta_c.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/economic/__pycache__/reproduction.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/economic/constants.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/economic/delta_c.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/economic/reproduction.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/economic/state_machine.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/ledger/README.md | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/ledger/__pycache__/block.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/ledger/__pycache__/block_store.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/ledger/__pycache__/hash_sync.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/ledger/__pycache__/pipeline.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/ledger/__pycache__/serialization.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/ledger/block.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/ledger/block_store.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/ledger/ctor_sort.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/ledger/hash_sync.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/ledger/pipeline.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/ledger/serialization.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/math/README.md | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/math/dro.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/math/fpe.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/math/sgf.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/README.md | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/__pycache__/vn.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/node/an.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/fi_node.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/ln.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/ptn.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/ren.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/sn.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/node/vn.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/runtime.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/state.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/sync/README.md | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/sync/__init__.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/sync/__pycache__/__init__.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/sync/__pycache__/shcm.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/influx/kernel/sync/ainf.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/sync/gde.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/sync/ros.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/influx/kernel/sync/shcm.py | ?? | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. |
| src/kernel/__init__.py | ?? | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |
| src/kernel/__pycache__/__init__.cpython-314.pyc | ?? | SHOULD_BE_GITIGNORED | Generated Python bytecode/cache artifact. |
| src/kernel/sync/__init__.py | ?? | NEEDS_REVIEW | Kernel tree change (deletion or addition) impacts core architecture and docs. |

## Category Totals

- SAFE_TO_KEEP: 3
- SAFE_TO_DELETE: 7
- NEEDS_REVIEW: 105
- SHOULD_BE_GITIGNORED: 77

## Priority Notes

- __pycache__ and *.pyc: large volume of churn; should be ignored globally to prevent noisy diffs.
- package-lock.json: review whether Node-based tooling is now part of release pipeline; otherwise remove.
- scripts/dev.sh: review for intended workflow and shell safety before commit.
- src/influx.egg-info/*: generated packaging metadata; ignore and avoid committing.
- Unexpected top-level files (56, PS, To, bash, python, and dotted filename) are classified SAFE_TO_DELETE pending owner confirmation.
- Deleted src/kernel docs/modules plus untracked src/influx/kernel tree strongly suggests a package migration; review as a single atomic move before merge.
