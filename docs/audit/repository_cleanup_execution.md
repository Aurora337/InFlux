# Repository Cleanup Execution Guide

**Source:** [repository_cleanup_plan.md](repository_cleanup_plan.md)  
**Date:** 2026-06-23  
**Analysis Purpose:** Categorize 189 dirty files into 4 actionable groups for safe, staged cleanup

---

## Executive Summary

**Total files analyzed:** 189 paths  

**Categorization:**
| Category | Count | Risk Level | Action |
|---|---|---|---|
| **1. Definitely Build Artifacts** | 40 | None | Immediate cleanup |
| **2. Definitely Runtime Artifacts** | 37 | None | Immediate cleanup |
| **3. Likely Accidental AI/Artifacts** | 7 | Low | Delete after confirmation |
| **4. Likely Legitimate Source Changes** | 105 | High | Code review + test validation |
| **TOTAL** | **189** | — | — |

---

## Category 1: Definitely Build Artifacts (40 files)

**Definition:** Compiled Python bytecode files generated during execution; safe to delete immediately.

**Cleanup Method:** Remove from git index, add pattern to .gitignore

### Python Bytecode Files by Location

**harness/ (10 files)**
```
harness/economic-stress/__pycache__/economic_verification_engine.cpython-314.pyc (M)
harness/economic-stress/__pycache__/metrics_collector.cpython-314.pyc (M)
harness/economic-stress/__pycache__/simulation_runner.cpython-314.pyc (M)
harness/economic-stress/__pycache__/stress_report.cpython-314.pyc (M)
harness/node-mesh-sim/__pycache__/consensus_simulator.cpython-314.pyc (M)
harness/node-mesh-sim/__pycache__/fault_injection_harness.cpython-314.pyc (M)
harness/replay-engine/__pycache__/replay_audit.cpython-314.pyc (M)
harness/replay-engine/__pycache__/replay_report.cpython-314.pyc (M)
harness/replay-engine/__pycache__/replay_runner.cpython-314.pyc (M)
harness/replay-engine/__pycache__/replay_scenario_runner.cpython-314.pyc (M)
```
**Action:** `git rm --cached -r harness/**/__pycache__`

**scripts/audit/ (2 files)**
```
scripts/audit/__pycache__/release_integrity_audit.cpython-314.pyc (M)
scripts/audit/__pycache__/repository_health_dashboard.cpython-314.pyc (M)
```
**Action:** `git rm --cached scripts/audit/__pycache__`

**tests/audit/ (2 files)**
```
tests/audit/__pycache__/test_release_integrity.cpython-314-pytest-9.1.1.pyc (M)
tests/audit/__pycache__/test_repository_health_dashboard.cpython-314-pytest-9.1.1.pyc (M)
```
**Action:** `git rm --cached tests/audit/__pycache__`

**tests/golden/ (24 files)**
```
tests/golden/__pycache__/test_consensus.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_consensus_failure.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_cross_env_reports.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_cross_env_reports.cpython-314.pyc (D)
tests/golden/__pycache__/test_economic_stress.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_economic_stress.cpython-314.pyc (D)
tests/golden/__pycache__/test_economic_verification.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_economic_verification.cpython-314.pyc (D)
tests/golden/__pycache__/test_fault_injection.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_fault_injection.cpython-314.pyc (D)
tests/golden/__pycache__/test_multi_node_consensus.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_multi_node_consensus.cpython-314.pyc (D)
tests/golden/__pycache__/test_network_simulation_integration.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_network_simulation_integration.cpython-314.pyc (D)
tests/golden/__pycache__/test_persistent_ledger.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_persistent_ledger.cpython-314.pyc (D)
tests/golden/__pycache__/test_replay_audit.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_replay_audit.cpython-314.pyc (D)
tests/golden/__pycache__/test_replay_scenarios.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_replay_scenarios.cpython-314.pyc (D)
tests/golden/__pycache__/test_replay_verification.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_replay_verification.cpython-314.pyc (D)
tests/golden/__pycache__/test_validator_consensus_agreement.cpython-314-pytest-9.1.1.pyc (M)
tests/golden/__pycache__/test_validator_consensus_agreement.cpython-314.pyc (D)
```
**Action:** `git rm --cached tests/golden/__pycache__`

**src/kernel/__pycache__/ (2 files, deleted)**
```
src/kernel/__pycache__/runtime.cpython-314.pyc (D)
src/kernel/__pycache__/state.cpython-314.pyc (D)
```
**Action:** `git rm src/kernel/__pycache__` (already deleted, clean up tracking)

**Top-level (1 file)**
```
__pycache__/compare_env_reports.cpython-314.pyc (untracked)
```
**Action:** `git clean -fdx __pycache__/`

**Subtotal: 40 .pyc files across multiple __pycache__ directories**

**Cleanup Command:**
```bash
git rm --cached -r __pycache__ harness/**/__pycache__ scripts/**/__pycache__ tests/**/__pycache__ src/**/__pycache__
git clean -fdx __pycache__
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
git add .gitignore
git commit -m "chore: exclude Python bytecode from version control"
```

---

## Category 2: Definitely Runtime Artifacts (37 files)

**Definition:** Generated packaging metadata files created during pip install or build; safe to delete immediately.

**Cleanup Method:** Remove from git index, add pattern to .gitignore

### Packaging Metadata

**src/influx.egg-info/ (5 untracked files)**
```
src/influx.egg-info/PKG-INFO
src/influx.egg-info/SOURCES.txt
src/influx.egg-info/dependency_links.txt
src/influx.egg-info/entry_points.txt
src/influx.egg-info/top_level.txt
```
**Why:** Auto-generated by `python setup.py develop` or `pip install -e .`  
**Risk:** None – safely deletable

### Python Cache in New influx Package Tree

**src/influx/__pycache__/ (2 untracked files)**
```
src/influx/__pycache__/__init__.cpython-314.pyc
src/influx/__pycache__/cli.cpython-314.pyc
```

**src/influx/kernel/__pycache__/ (30 untracked files across submodules)**
```
src/influx/kernel/__pycache__/__init__.cpython-314.pyc
src/influx/kernel/__pycache__/runtime.cpython-314.pyc
src/influx/kernel/__pycache__/state.cpython-314.pyc
src/influx/kernel/alignment/__pycache__/ (5 files)
src/influx/kernel/economic/__pycache__/ (6 files)
src/influx/kernel/ledger/__pycache__/ (6 files)
src/influx/kernel/node/__pycache__/ (5 files)
src/influx/kernel/sync/__pycache__/ (4 files)
```

**Cleanup Command:**
```bash
git rm --cached -r src/influx.egg-info/ src/influx/__pycache__ src/influx/kernel/__pycache__
git clean -fdx src/influx.egg-info/ src/influx/**/__pycache__
echo "*.egg-info/" >> .gitignore
git add .gitignore
git commit -m "chore: exclude packaging metadata and generated caches from version control"
```

**Total Category 2: 37 files**

---

## Category 3: Likely Accidental AI/Terminal Artifacts (7 files)

**Definition:** Top-level files with no semantic meaning, likely created by accidental command execution or AI context pollution.

**Risk Level:** Low – clearly not part of project source

### Files to Delete

| Path | Evidence of Accident | Action |
|---|---|---|
| `56` | Numeric filename, meaningless | `git rm --force 56` |
| `PS` | Resembles Windows command | `git rm --force PS` |
| `To` | Incomplete word, likely copy/paste error | `git rm --force To` |
| `bash` | Resembles shell executable reference | `git rm --force bash` |
| `python` | Resembles Python executable reference | `git rm --force python` |
| `........................................................` | Pure whitespace/dots, clearly accidental | `git rm --force "........................................................"` |
| `.vscode/.easycpp` | Editor plugin artifact; not part of project | `git rm --force .vscode/.easycpp` |

**Why These Are Accidents:**
- Zero semantic relationship to InFlux repository
- No sensible file extension
- Appear at top level (not in organized subdirectories)
- Untracked or carelessly committed

**Cleanup Command:**
```bash
git rm --force 56 PS To bash python ".........................................................." .vscode/.easycpp
git commit -m "chore: remove accidental top-level artifacts"
```

**Total Category 3: 7 files**

**Risk:** None – safe to delete

---

## Category 4: Likely Legitimate Source Changes (105 files)

**Definition:** Files with semantic meaning to the project: source code, tests, and package migrations that require code review before merge.

**Risk Level:** High – contains functional logic and architectural changes

### Subcategory 4A: Harness System Changes (8 Python files)

**Economic Verification Subsystem (2 files)**
```
harness/economic-stress/economic_verification_engine.py (M)
harness/economic-stress/simulation_runner.py (M)
```
**Review Criteria:**
- Check for logic correctness in verification engine
- Validate simulation runner handles edge cases
- Run: `pytest tests/audit/economic_stress* -xvs`

**Node Mesh Simulation Subsystem (2 files)**
```
harness/node-mesh-sim/consensus_simulator.py (M)
harness/node-mesh-sim/fault_injection_harness.py (M)
```
**Review Criteria:**
- Validate consensus algorithm implementation
- Check fault injection coverage and correctness
- Run: `pytest tests/audit/node_mesh* -xvs`

**Replay Engine Subsystem (4 files)**
```
harness/replay-engine/environment_report.py (M)
harness/replay-engine/replay_audit.py (M)
harness/replay-engine/replay_runner.py (M)
harness/replay-engine/replay_scenario_runner.py (M)
```
**Review Criteria:**
- Validate report format and accuracy
- Check audit log correctness
- Ensure scenario execution completeness
- Run: `pytest tests/golden/replay* -xvs`

### Subcategory 4B: Core Script Changes (4 Python files)

| Path | Purpose | Review Criteria |
|---|---|---|
| `multi_node_consensus.py` (M) | Multi-node consensus orchestration | Validate logic; check state consistency |
| `replay_audit.py` (M) | Replay audit logic | Verify audit completeness |
| `verify_ledger.py` (M) | Ledger integrity verification | Check all verification paths |
| `scripts/generate_demo_ledger.py` (M) | Demo ledger generation | Validate deterministic output |

**Run:** `pytest tests/golden/consensus*.py tests/golden/replay*.py tests/golden/persistent*.py -xvs`

### Subcategory 4C: Test Suite Changes (11 test files)

All modified test files in `tests/golden/`:
```
test_consensus.py (M)
test_consensus_failure.py (M)
test_economic_stress.py (M)
test_multi_node_consensus.py (M)
test_network_simulation_integration.py (M)
test_persistent_ledger.py (M)
test_replay_audit.py (M)
test_replay_verification.py (M)
test_validator_consensus_agreement.py (M)
test_validator_consensus_mismatch.py (M)
test_validator_hash_agreement.py (M)
```

**Review Criteria:**
- Ensure all tests still pass: `pytest tests/golden/ -v`
- Check for new test coverage or changed assertions
- Validate no test regressions

### Subcategory 4D: Project Configuration (2 files)

| Path | Type | Status | Review Criteria |
|---|---|---|---|
| `package-lock.json` (untracked) | Node lockfile | **Needs Decision** | Is Node.js now part of build pipeline? If added recently, document in README. If accidental, delete. |
| `scripts/dev.sh` (untracked) | Shell helper | **Needs Security Review** | Review shell script for: correct permissions, no dangerous commands, proper error handling. If approved, add to repo; if not, delete. |

### Subcategory 4E: Kernel Namespace Migration (68 untracked files)

**Status: ARCHITECTURAL RISK – See Section D for details**

**New influx package tree (68 files):**
```
src/influx/__init__.py (untracked)
src/influx/cli.py (untracked)
src/influx/kernel/ (complete tree, 68 files)
  ├── README.md
  ├── __init__.py
  ├── alignment/ (5 files)
  ├── economic/ (6 files)
  ├── ledger/ (8 files)
  ├── math/ (5 files)
  ├── node/ (9 files)
  └── sync/ (6 files)
```

**Evidence of Migration:**
- 58 files deleted from `src/kernel/` (M, D status)
- 62 files untracked under `src/influx/kernel/` (mirror of deletions)
- 2 stub files (`src/kernel/__init__.py`, `src/kernel/sync/__init__.py`) untracked

**Migration Intent Assessment:**
- **Most Likely:** Deliberate namespace refactor from `src.kernel` → `src.influx.kernel`
- **Evidence For:** Complete parallel tree structure, symmetric deletions and additions
- **Evidence Against:** Untracked instead of committed; no migration commit message; incomplete .gitignore update

**Critical Review Points:**
1. Is this a **completed migration** or **work-in-progress**?
2. Are **all imports updated** to reference new namespace?
3. Do **all tests pass** against new structure?
4. Are **deleted README files replicated** in new location?

---

## Category 4 Execution Plan

### Phase 1: Fast Track – Tests (11 files + 4 scripts)
```bash
# Run affected test suite
pytest tests/golden/ -v --tb=short

# Run harness tests
pytest tests/audit/ -v --tb=short

# Run core scripts with validation
python scripts/generate_demo_ledger.py
python verify_ledger.py
python replay_audit.py
```

**Decision Gate:** If all tests pass → proceed to Phase 2. If failures → request fixes before merge.

### Phase 2: Configuration Review (2 files)
```bash
# Analyze package-lock.json
ls -la package-lock.json  # Check modification date
git diff package-lock.json | head -20  # See changes

# Inspect dev.sh
cat scripts/dev.sh  # Manual review for security
shellcheck scripts/dev.sh 2>/dev/null || echo "Install shellcheck for validation"
```

**Decision Gate:** 
- If `package-lock.json` is intentional (Node added to pipeline) → document in README
- If `package-lock.json` is accidental → delete
- If `scripts/dev.sh` passes security review → merge; otherwise delete or request fixes

### Phase 3: Kernel Migration Review (68 files) – **BLOCKING**
```bash
# Verify structural completeness
diff -r src/kernel/ src/influx/kernel/ | head -30  # Show differences

# Find broken imports
grep -r "from src.kernel" . --include="*.py" | head -20
grep -r "from src\.kernel" . --include="*.py" | head -20

# Run full test suite with new namespace
pytest tests/ -v --tb=short

# Check documentation consistency
diff src/kernel/README.md src/influx/kernel/README.md
diff src/kernel/*/README.md src/influx/kernel/*/README.md
```

**Decision Gate:** 
- **STOP** if any imports still reference old `src.kernel` namespace
- **STOP** if tests fail with new structure
- **STOP** if documentation is missing or inconsistent
- **Only proceed** when all imports updated, tests pass 100%, and docs verified

---

## Execution Sequence (Recommended)

### Phase Alpha: Safe Cleanup (Category 1 + 2 + 3) – **IMMEDIATE**
```bash
# Remove build artifacts
git rm --cached -r __pycache__ **/__pycache__ *.pyc

# Remove runtime artifacts  
git rm --cached -r src/influx.egg-info/ src/influx/**/__pycache__

# Remove accidental files
git rm --force 56 PS To bash python "........................................................." .vscode/.easycpp

# Update .gitignore
cat >> .gitignore << 'EOF'
__pycache__/
*.pyc
*.egg-info/
dist/
build/
EOF

git add .gitignore
git commit -m "chore: clean repository and exclude generated artifacts"
```

**Risk:** None – all safe deletions  
**Expected Result:** 84 files removed, repository size reduced

### Phase Beta: Code Review (Category 4A-4D) – **CONDITIONAL**
```bash
# Run test suite
pytest tests/ -v

# Review harness/test changes
git diff HEAD~1 harness/ tests/golden/ scripts/

# Inspect config changes
git diff HEAD~1 package-lock.json scripts/dev.sh

# Validate kernel migration
grep -r "from src.kernel" . --include="*.py"
```

**Risk:** Medium – depends on code quality  
**Decision Point:** Approve/request fixes per review findings

### Phase Gamma: Kernel Migration (Category 4E) – **BLOCKING**
```bash
# Verify kernel migration completeness
python3 << 'EOF'
import os
import sys

src_kernel = {f for f in os.walk('src/kernel/') if f[0].endswith('.py')}
influx_kernel = {f for f in os.walk('src/influx/kernel/') if f[0].endswith('.py')}

missing = src_kernel - influx_kernel
if missing:
    print("MISSING FILES IN MIGRATION:")
    for f in missing:
        print(f"  {f}")
    sys.exit(1)
else:
    print("Migration structure complete")
EOF

# Test with new namespace
pytest tests/ -v

# Commit migration
git add src/influx/
git rm -r src/kernel/
git commit -m "refactor: migrate kernel modules to influx namespace"
```

**Risk:** High – architectural change  
**Decision Point:** DO NOT MERGE until kernel migration validation passes 100%

---

## Summary Decision Matrix

| Category | Files | Status | Risk | Gate | Owner |
|---|---|---|---|---|---|
| **1. Build Artifacts** | 40 | Ready | None | Auto | DevOps |
| **2. Runtime Artifacts** | 37 | Ready | None | Auto | DevOps |
| **3. Accidental Files** | 7 | Ready | Low | Confirm | DevOps |
| **4A. Harness Changes** | 8 | Review | Medium | Tests pass | Tech Lead |
| **4B. Core Scripts** | 4 | Review | Medium | Tests pass | Tech Lead |
| **4C. Test Suite** | 11 | Review | Medium | Tests pass | Tech Lead |
| **4D. Config Changes** | 2 | Review | Medium | Decision | Tech Lead |
| **4E. Kernel Migration** | 68 | **BLOCKED** | High | 100% validation | Architect |
| **TOTAL** | **189** | — | — | — | — |

---

## References

- Cleanup Plan: [repository_cleanup_plan.md](repository_cleanup_plan.md)
- Hygiene Report: [repository_hygiene_report.md](repository_hygiene_report.md)
- Audit Reports: [release_integrity_report.json](release_integrity_report.json), [repository_health.json](repository_health.json)
