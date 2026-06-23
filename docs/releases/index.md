# InFlux Release Notes Index

Readable milestone history for the Sync Ops Audit Ladder and earlier release milestones.

## Milestones

### v0.x Series - Foundation

- [v0.1 Release Notes](v0.1-release-notes.md): deterministic kernel foundation.
- [v0.2 Release Notes](v0.2-release-notes.md): replay verification and ledger integrity.
- [v0.3 Release Notes](v0.3-release-notes.md): multi-node consensus validation.
- [v0.4 Release Notes](v0.4-release-notes.md): resilience testing under injected faults.
- [v0.5 Release Notes](v0.5-release-notes.md): cross-environment determinism validation.
- [v0.6 Release Notes](v0.6-release-notes.md): economic verification and consolidated audit packaging.

### v1.x Series - Sync Ops Audit Ladder

**Progressive framework for autonomous release governance**

- [v1.1.1-release-notes.md](v1.1.1-release-notes.md): Release Integrity Audit + Repository Health Dashboard ✅
- [v1.1.2-release-notes.md](v1.1.2-release-notes.md): Release Readiness Audit (7-point gate) ✅
- [v1.1.3-release-notes.md](SYNC_OPS_AUDIT_LADDER.md): Continuous Audit Monitor (drift detection) ✅
- [v1.1.4-release-notes.md](v1.1.4-release-notes.md): Automated Release Validation (aggregation layer) ✅
- v1.1.5-release-notes.md: Regression Detection (historical trends) ▶
- v1.1.6-release-notes.md: Release Certification (full automation) 📋
- v1.2.0-release-notes.md: Autonomous Release Governance (self-healing) 🎯

**Key Features**:
- Deterministic audit pipeline (read JSON, produce JSON)
- GitHub Actions CI/CD integration
- Release approval gate with score-based decisions
- Drift detection for continuous monitoring

## Audit Ladder Architecture

```
v1.1.1: Release Integrity + Health
        ↓
v1.1.2: Release Readiness (7-point)
        ↓
v1.1.3: Continuous Monitoring (drift)
        ↓
v1.1.4: Automated Validation (aggregation)
        ↓
v1.1.5: Regression Detection (trends)
        ↓
v1.1.6: Release Certification (automation)
        ↓
v1.2.0: Autonomous Governance (self-healing)
```

## Suggested Next Milestone
- v1.1.5 Regression Detection: historical trend analysis for validation_score and release_approval drift.

## Audit Regression Detection

v1.1.5 introduces a deterministic regression gate that compares the current
audit layer outputs against validated baselines.

Primary report signals:
- regression_detected
- regression_score
- baseline_valid
