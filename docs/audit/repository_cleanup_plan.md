# Repository Cleanup Plan

**Derived from:** [docs/audit/repository_hygiene_report.md](repository_hygiene_report.md)  
**Date:** 2026-06-23  
**Branch:** v1.1.1-sync-ops-audit  
**Total items requiring action:** 189 paths  

---

## Executive Summary

This cleanup plan organizes 189 dirty repository paths into actionable groups:
- **Section A:** 7 paths can be deleted immediately (accidental top-level artifacts)
- **Section B:** 77 paths should be excluded from version control via .gitignore (generated Python bytecode and packaging metadata)
- **Section C:** 105 paths require manual review (source code changes, new package migrations, helper scripts)
- **Section D:** 62 paths represent critical architectural risk (kernel deletion + namespace migration)

---

## Section A: Immediate Deletions

These paths are accidental, editor-local, or unrelated to the project and can be safely removed.

### Top-Level Unexpected Artifacts

| Path | Classification | Reason | Recommended Action |
|---|---|---|---|
| `56` | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. | `git rm --force 56` |
| `PS` | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. | `git rm --force PS` |
| `To` | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. | `git rm --force To` |
| `bash` | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. | `git rm --force bash` |
| `python` | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. | `git rm --force python` |
| `........................................................` | SAFE_TO_DELETE | Unexpected top-level artifact with no clear project role. | `git rm --force "........................................................"` |

### Editor/IDE Artifacts

| Path | Classification | Reason | Recommended Action |
|---|---|---|---|
| `.vscode/.easycpp` | SAFE_TO_DELETE | Editor-local artifact not required for project source control. | `git rm --force .vscode/.easycpp` |

**Subtotal: 7 deletions** (all untracked, safe to remove via git rm --force)

---

## Section B: Add To .gitignore

These paths are generated build/runtime artifacts that should be excluded from version control. Update `.gitignore` to prevent future commits of these patterns.

### Python Bytecode & Cache Files

**Pattern to add to .gitignore:**
```
__pycache__/
*.pyc
*.pyo
*.pyd
*.so
*.egg-info/
```

#### Current tracked instances requiring cleanup:

**harness/economic-stress/__pycache__/**
- `harness/economic-stress/__pycache__/economic_verification_engine.cpython-314.pyc` (modified)
- `harness/economic-stress/__pycache__/metrics_collector.cpython-314.pyc` (modified)
- `harness/economic-stress/__pycache__/simulation_runner.cpython-314.pyc` (modified)
- `harness/economic-stress/__pycache__/stress_report.cpython-314.pyc` (modified)

**harness/node-mesh-sim/__pycache__/**
- `harness/node-mesh-sim/__pycache__/consensus_simulator.cpython-314.pyc` (modified)
- `harness/node-mesh-sim/__pycache__/fault_injection_harness.cpython-314.pyc` (modified)

**harness/replay-engine/__pycache__/**
- `harness/replay-engine/__pycache__/environment_report.cpython-314.pyc` (deleted)
- `harness/replay-engine/__pycache__/replay_audit.cpython-314.pyc` (modified)
- `harness/replay-engine/__pycache__/replay_report.cpython-314.pyc` (modified)
- `harness/replay-engine/__pycache__/replay_runner.cpython-314.pyc` (modified)
- `harness/replay-engine/__pycache__/replay_scenario_runner.cpython-314.pyc` (modified)
- `harness/replay-engine/__pycache__/replay_store.cpython-314.pyc` (modified)

**scripts/audit/__pycache__/**
- `scripts/audit/__pycache__/release_integrity_audit.cpython-314.pyc` (modified)
- `scripts/audit/__pycache__/repository_health_dashboard.cpython-314.pyc` (modified)

**tests/audit/__pycache__/**
- `tests/audit/__pycache__/test_release_integrity.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/audit/__pycache__/test_repository_health_dashboard.cpython-314-pytest-9.1.1.pyc` (modified)

**tests/golden/__pycache__/**
- `tests/golden/__pycache__/test_consensus.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_consensus_failure.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_cross_env_reports.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_cross_env_reports.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_economic_stress.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_economic_stress.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_economic_verification.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_economic_verification.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_fault_injection.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_fault_injection.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_multi_node_consensus.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_multi_node_consensus.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_network_simulation_integration.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_network_simulation_integration.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_persistent_ledger.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_persistent_ledger.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_replay_audit.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_replay_audit.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_replay_scenarios.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_replay_scenarios.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_replay_verification.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_replay_verification.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_validator_consensus_agreement.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_validator_consensus_agreement.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_validator_consensus_mismatch.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_validator_consensus_mismatch.cpython-314.pyc` (deleted)
- `tests/golden/__pycache__/test_validator_hash_agreement.cpython-314-pytest-9.1.1.pyc` (modified)
- `tests/golden/__pycache__/test_validator_hash_agreement.cpython-314.pyc` (deleted)

**src/kernel/__pycache__/**
- `src/kernel/__pycache__/runtime.cpython-314.pyc` (deleted)
- `src/kernel/__pycache__/state.cpython-314.pyc` (deleted)
- `src/kernel/__pycache__/shcm.cpython-314.pyc` (deleted)
- `src/kernel/node/__pycache__/vn.cpython-314.pyc` (deleted)

**Top-level**
- `__pycache__/compare_env_reports.cpython-314.pyc` (untracked)

**src/influx/__pycache__/**
- `src/influx/__pycache__/__init__.cpython-314.pyc` (untracked)
- `src/influx/__pycache__/cli.cpython-314.pyc` (untracked)

**src/influx/kernel/__pycache__/**
- `src/influx/kernel/__pycache__/__init__.cpython-314.pyc` (untracked)
- `src/influx/kernel/__pycache__/runtime.cpython-314.pyc` (untracked)
- `src/influx/kernel/__pycache__/state.cpython-314.pyc` (untracked)
- `src/influx/kernel/alignment/__pycache__/` – (untracked, multiple .pyc files)
- `src/influx/kernel/economic/__pycache__/` – (untracked, multiple .pyc files)
- `src/influx/kernel/ledger/__pycache__/` – (untracked, multiple .pyc files)
- `src/influx/kernel/node/__pycache__/` – (untracked, multiple .pyc files)
- `src/influx/kernel/sync/__pycache__/` – (untracked, multiple .pyc files)

### Packaging Metadata

**Pattern to add to .gitignore:**
```
*.egg-info/
dist/
build/
```

#### Current tracked instances:

- `src/influx.egg-info/PKG-INFO` (untracked)
- `src/influx.egg-info/SOURCES.txt` (untracked)
- `src/influx.egg-info/dependency_links.txt` (untracked)
- `src/influx.egg-info/entry_points.txt` (untracked)
- `src/influx.egg-info/top_level.txt` (untracked)

**Subtotal: 77 items** (40 tracked .pyc files + 31 untracked .pyc files + 6 untracked egg-info files)

**Recommended cleanup:**
1. Add patterns to `.gitignore`
2. Run `git rm --cached -r __pycache__ src/**/__pycache__ *.pyc src/influx.egg-info/`
3. Run `git clean -fdx` to remove untracked cache files
4. Commit with message: `chore: exclude Python bytecode and packaging metadata from version control`

---

## Section C: Manual Review Required

These items require code review, functional testing, or architectural decision-making before they can be merged.

### Source Code and Test Changes (25 files)

**Harness System Files:**
| Path | Classification | Reason | Recommended Action |
|---|---|---|---|
| `harness/economic-stress/economic_verification_engine.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate economic verification logic. |
| `harness/economic-stress/simulation_runner.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate simulation execution. |
| `harness/node-mesh-sim/consensus_simulator.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate consensus simulation. |
| `harness/node-mesh-sim/fault_injection_harness.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate fault injection. |
| `harness/replay-engine/environment_report.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate replay report generation. |
| `harness/replay-engine/replay_audit.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate replay audit logic. |
| `harness/replay-engine/replay_runner.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate replay execution. |
| `harness/replay-engine/replay_scenario_runner.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate scenario runner. |

**Core/Top-Level Scripts:**
| Path | Classification | Reason | Recommended Action |
|---|---|---|---|
| `multi_node_consensus.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate multi-node consensus logic. |
| `replay_audit.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate replay audit. |
| `verify_ledger.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate ledger verification. |
| `scripts/generate_demo_ledger.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run unit tests; validate demo ledger generation. |

**Test Files (11 modified):**
| Path | Classification | Reason | Recommended Action |
|---|---|---|---|
| `tests/golden/test_consensus.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate consensus tests pass. |
| `tests/golden/test_consensus_failure.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate failure cases. |
| `tests/golden/test_economic_stress.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate economic stress tests. |
| `tests/golden/test_multi_node_consensus.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate multi-node tests. |
| `tests/golden/test_network_simulation_integration.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate network simulation. |
| `tests/golden/test_persistent_ledger.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate ledger persistence. |
| `tests/golden/test_replay_audit.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate replay audit tests. |
| `tests/golden/test_replay_verification.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate replay verification. |
| `tests/golden/test_validator_consensus_agreement.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate validator agreement. |
| `tests/golden/test_validator_consensus_mismatch.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate mismatch detection. |
| `tests/golden/test_validator_hash_agreement.py` | NEEDS_REVIEW | Source/test code changed; requires functional review. | Run pytest; validate hash agreement. |

### Project Configuration & Tooling (2 files)

| Path | Classification | Reason | Recommended Action |
|---|---|---|---|
| `package-lock.json` | NEEDS_REVIEW | Node lockfile in primarily Python repo; keep only if Node toolchain is intentional. | Determine if Node.js is now part of build pipeline; if not, delete. If yes, document in README. |
| `scripts/dev.sh` | NEEDS_REVIEW | New helper script; verify ownership, usage, and security before keeping. | Code review for shell security; document usage; add to README if approved. |

### Kernel Namespace Migration (68 untracked files)

**New influx package tree likely part of kernel namespace migration:**

| Path | Classification | Reason | Recommended Action |
|---|---|---|---|
| `src/influx/__init__.py` | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. | Verify this is a deliberate refactor; ensure all imports are updated. |
| `src/influx/cli.py` | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. | Review CLI implementation; validate entry point configuration. |
| `src/influx/kernel/README.md` | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. | Validate README reflects new location and purpose. |
| `src/influx/kernel/__init__.py` | NEEDS_REVIEW | New package tree likely part of kernel namespace migration; validate move completeness. | Verify module exports and version info. |

**Full tree under src/influx/kernel/:**
- Alignment submodule: README, __init__, classifier, router, tags, validator (6 files)
- Economic submodule: README, __init__, constants, delta_c, reproduction, state_machine (6 files)
- Ledger submodule: README, __init__, block, block_store, ctor_sort, hash_sync, pipeline, serialization (8 files)
- Math submodule: README, __init__, dro, fpe, sgf (5 files)
- Node submodule: README, __init__, an, fi_node, ln, ptn, ren, sn, vn (9 files)
- Sync submodule: README, __init__, ainf, gde, ros, shcm (6 files)

**Subtotal: 68 untracked files** representing full kernel tree duplication/migration under new namespace

**Recommended action for kernel migration:**
1. Verify completeness: ensure all deleted src/kernel/* files are represented under src/influx/kernel/*
2. Validate import paths: update all imports to use `from src.influx.kernel.*` instead of `from src.kernel.*`
3. Run full test suite: `pytest tests/ -v`
4. Confirm no broken imports: search codebase for references to `src.kernel` or `src/kernel`
5. Once validated, commit as atomic operation: `git add src/influx/kernel && git commit -m "refactor: migrate kernel modules to influx namespace"`

**Subtotal: 105 items** (25 source/test files + 2 config items + 68 kernel migration files + 10 kernel stubs)

---

## Section D: Critical Repository Risks

These items represent **high-risk structural changes** requiring careful review before merge. The kernel module deletion combined with the new influx namespace suggests an ongoing migration that could break the repository if incomplete or untested.

### Deleted Kernel Documentation (4 files)

Core architecture documentation has been deleted without clear migration path:

| Path | Status | Issue | Mitigation |
|---|---|---|---|
| `src/kernel/README.md` | Deleted | Core architecture guide removed. | Verify equivalent docs exist in src/influx/kernel/README.md. |
| `src/kernel/alignment/README.md` | Deleted | Alignment module documentation removed. | Verify equivalent docs exist. |
| `src/kernel/economic/README.md` | Deleted | Economic module documentation removed. | Verify equivalent docs exist. |
| `src/kernel/ledger/README.md` | Deleted | Ledger module documentation removed. | Verify equivalent docs exist. |
| `src/kernel/math/README.md` | Deleted | Math module documentation removed. | Verify equivalent docs exist. |
| `src/kernel/node/README.md` | Deleted | Node module documentation removed. | Verify equivalent docs exist. |
| `src/kernel/sync/README.md` | Deleted | Sync module documentation removed. | Verify equivalent docs exist. |

### Deleted Kernel Implementation (58 files)

Core kernel modules entirely deleted:

**Alignment subsystem:** 5 files deleted
- `src/kernel/alignment/classifier.py`
- `src/kernel/alignment/router.py`
- `src/kernel/alignment/tags.py`
- `src/kernel/alignment/validator.py`

**Economic subsystem:** 4 files deleted
- `src/kernel/economic/constants.py`
- `src/kernel/economic/delta_c.py`
- `src/kernel/economic/reproduction.py`
- `src/kernel/economic/state_machine.py`

**Ledger subsystem:** 6 files deleted
- `src/kernel/ledger/block.py`
- `src/kernel/ledger/block_store.py`
- `src/kernel/ledger/ctor_sort.py`
- `src/kernel/ledger/hash_sync.py`
- `src/kernel/ledger/pipeline.py`
- `src/kernel/ledger/serialization.py`

**Math subsystem:** 3 files deleted
- `src/kernel/math/dro.py`
- `src/kernel/math/fpe.py`
- `src/kernel/math/sgf.py`

**Node subsystem:** 7 files deleted
- `src/kernel/node/an.py`
- `src/kernel/node/fi_node.py`
- `src/kernel/node/ln.py`
- `src/kernel/node/ptn.py`
- `src/kernel/node/ren.py`
- `src/kernel/node/sn.py`
- `src/kernel/node/vn.py`

**Sync subsystem:** 4 files deleted
- `src/kernel/sync/ainf.py`
- `src/kernel/sync/gde.py`
- `src/kernel/sync/ros.py`
- `src/kernel/sync/shcm.py`

**Runtime core:** 2 files deleted
- `src/kernel/runtime.py`
- `src/kernel/state.py`

### Kernel Namespace Migration (62 untracked files in new location)

All deleted files appear to have untracked equivalents under `src/influx/kernel/`:
- `src/influx/kernel/alignment/` (5 files)
- `src/influx/kernel/economic/` (4 files)
- `src/influx/kernel/ledger/` (6 files)
- `src/influx/kernel/math/` (3 files)
- `src/influx/kernel/node/` (7 files)
- `src/influx/kernel/sync/` (4 files)
- `src/influx/kernel/{runtime.py, state.py}` (2 files)
- Plus init stubs and bytecode

### Incomplete Migration Indicators

| Risk Factor | Evidence | Impact |
|---|---|---|
| **Missing .gitignore commit** | Kernel pycache deleted, influx pycache untracked | Tests may run stale bytecode; builds non-deterministic. |
| **Untracked migration** | New files untracked instead of moved | Import failures if git history broken; migration incomplete. |
| **No refactoring markers** | No commits documenting migration strategy | Difficult to audit completeness; hard to debug breakage. |
| **Kernel stub files** | `src/kernel/__init__.py` and `src/kernel/sync/__init__.py` untracked | Suggests partial migration; unknown intent. |

### Recommended Action for Section D

**STOP and do NOT merge this branch until:**

1. **Confirm migration intent:** Is this a deliberate namespace refactor from `src.kernel` to `src.influx.kernel`, or accidental deletion?

2. **Validate completeness:** For every deleted `src/kernel/*` file, confirm identical copy exists under `src/influx/kernel/*` with correct imports.

3. **Test all imports:** 
   ```bash
   grep -r "from src.kernel" . --include="*.py"
   grep -r "import src.kernel" . --include="*.py"
   grep -r "from src\.kernel" . --include="*.py"
   grep -r "import src\.kernel" . --include="*.py"
   ```
   All results must be updated to reference `src.influx.kernel` or deleted if no longer needed.

4. **Run full test suite:** `pytest tests/ -v` must pass 100%.

5. **Audit documentation:** Verify all deleted README.md files have equivalents and all import examples updated.

6. **Commit atomically:** Once validated, restructure as a single clean commit:
   ```bash
   git add src/influx/
   git rm -r src/kernel/
   git commit -m "refactor: migrate kernel modules to influx namespace under src/"
   ```

**Subtotal: 62 items** (58 deleted implementation files + 4 deleted docs + 62 untracked migration files in new location + 2 kernel stub files)

---

## Cleanup Workflow

### Phase 1: Immediate Cleanup (Section A + B)
```bash
# Remove accidental top-level artifacts
git rm --force 56 PS To bash python "........................................................" .vscode/.easycpp

# Remove cached bytecode and egg-info
git rm --cached -r __pycache__ src/**/__pycache__ *.pyc
git rm --cached -r src/influx.egg-info/

# Update .gitignore
cat >> .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.so
*.egg-info/
dist/
build/
EOF

# Clean untracked artifacts
git clean -fdx -- __pycache__ src/**/__pycache__ src/**/*.pyc

# Commit
git add .gitignore
git commit -m "chore: clean repository and exclude generated artifacts"
```

### Phase 2: Code Review (Section C)
- Run test suite: `pytest tests/ -xvs`
- Review functional changes in harness and test files
- Validate package-lock.json and scripts/dev.sh
- Approve or request fixes

### Phase 3: Architecture Review (Section D)
- **BLOCKING:** Resolve kernel migration intent and completeness
- Validate all imports updated
- Ensure test suite passes
- Document migration in CHANGELOG

---

## Summary Table

| Section | Count | Status | Owner |
|---|---|---|---|
| **A – Immediate Deletions** | 7 | Ready to execute | DevOps |
| **B – Add To .gitignore** | 77 | Ready to execute | DevOps |
| **C – Manual Review** | 105 | Pending code review | Tech Lead |
| **D – Critical Risks** | 62 | **BLOCKING** – requires architecture review | Architect |
| **TOTAL** | **251** | **189 paths in git status** | — |

---

## References

- Hygiene Report: [docs/audit/repository_hygiene_report.md](repository_hygiene_report.md)
- Related Audits: [docs/audit/release_integrity_report.json](release_integrity_report.json) | [docs/audit/repository_health.json](repository_health.json)
