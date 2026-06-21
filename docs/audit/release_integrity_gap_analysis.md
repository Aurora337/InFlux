# Release Integrity Gap Analysis (v1.1.1 Slice 1)

This document analyzes why `audit_valid` is `false` for the repository release-integrity audit, without proposing code changes or commits.

Source of truth:
- `docs/audit/release_integrity_report.json`
- `scripts/audit/release_integrity_audit.py`
- `docs/releases/*.md`

---

## Audit summary

From `docs/audit/release_integrity_report.json`:
- `audit_valid: false`
- `integrity_score: 1.0`
- `tags_checked: 35`
- `tags_valid: 35`

So:
- **Tag integrity is good** (all tags resolve and point to reachable commits).
- **Release-doc integrity is not good** (the audit cannot reconcile tags with release-notes milestones).

---

## 1) Missing release note files (as interpreted by the audit)

The audit reports `missing_release_notes`:
- `v0.1`
- `v1.0.0`
- `v1.0.1`
- `v1.0.2`
- `v1.0.3`
- `v1.0.4`
- `v1.0.5`
- `v1.0.6`
- `v1.0.7`
- `v1.0.8`
- `v1.0.9`
- `v1.1.0`

### Do these files truly not exist?

They **do exist in `docs/releases/`**:
- `v0.1` → `docs/releases/v0.1-release-notes.md`
- `v1.0.0` → `docs/releases/v1.0.0-release-notes.md`
- `v1.1.0` → `docs/releases/v1.1.0-release-notes.md`

Therefore, the audit’s *reported missing notes* appear to be **a mapping/normalization mismatch**, not a filesystem/documentation absence.

---

## 2) Orphaned tags

The audit reports `orphaned_tags`:
- `v0.1.0-kernel`
- `v0.2.0-replay`
- `v0.3.0-consensus`
- `v0.4.0-resilience`
- `v0.5.0-cross-platform`
- `v0.6.0-economic`
- `v0.6.0-economic-verification`
- `v0.7.5-testnet-validation`
- `v0.8.2-state-synchronization`
- `v0.8.3-staggered-catchup`
- `v0.8.4-dual-offline-recovery`
- `v0.8.5-sync-hardening`
- `v0.8.6-sync-resilience`
- `v0.8.7-sync-orchestration`
- `v0.8.8-sync-operations`
- `v0.8.9-sync-operations-handoff`
- `v0.9.0-sync-ops-stabilization`
- `v0.9.1-sync-ops-hardening`
- `v0.9.2-sync-ops-assurance`
- `v0.9.3-sync-ops-governance`
- `v0.9.4-sync-ops-finalization`
- `v0.9.5-sync-ops-finalization`
- `v0.9.6-sync-ops-finalization`

### Why are these orphaned?

In `scripts/audit/release_integrity_audit.py`:
- The audit only attempts release-note mapping for tags that match the regex:
  - `is_tag_version_tag(tag)` returns `True` for `^v?\d+\.\d+(?:\.\d+)?$`
  - This means it allows tags like `v1.0` or `v1.0.1`, but **not** tags with qualifiers like `v0.1.0-kernel`.
- For qualified tags containing suffixes (e.g. `-kernel`, `-replay`, `-consensus`), the audit treats them as **unmapped** and therefore **orphaned**.

This is consistent with the list above: all orphaned tags include a `-<qualifier>` suffix.

---

## 3) Root cause hypothesis: tag→release-note mapping is too strict

The audit’s mapping logic uses milestone grouping like:
- expected release-note milestone for `vX.Y.Z` (or `vX.Y`) is derived from `X.Y`.

However, the reported `missing_release_notes` strongly suggests a second mismatch:
- the audit is treating milestone keys such as `"v1.0.0"` and expecting a release note filename keyed exactly to those milestones,
- while the repository’s release-notes filenames are present.

Given that:
- tag integrity is perfect (`tags_valid == tags_checked`),
- `docs/releases/*-release-notes.md` for the “missing” milestones do exist,

the most likely explanation is:
1. The mapping step is deriving an **unexpected milestone key** from each tag.
2. Or, the code is checking existence using a **key format** that does not match the filesystem’s filename-derived keys.

In other words: **tag normalization is not aligning with milestone filenames**.

Separately, qualified tags (e.g. `v0.1.0-kernel`) are treated as orphaned because the audit currently refuses to map tags with suffixes.

---

## 4) Recommended fixes (no code changes performed here)

Two classes of remediation are recommended; either may be sufficient depending on what the audit contract expects.

### Fix option A — Smarter tag normalization (recommended)

Teach the audit to normalize tags with qualifiers into milestone versions before checking release notes.

Examples:
- `v0.1.0-kernel` → milestone `v0.1`
- `v0.2.0-replay` → milestone `v0.2`
- `v0.6.0-economic-verification` → milestone `v0.6`
- `v0.7.5-testnet-validation` → milestone `v0.7` (if/when milestone notes exist)

Then:
- compute the release-note expected filename from the normalized milestone,
- check the existence of that normalized milestone’s release note.

This directly addresses both:
- orphaned tags (by mapping qualified tags)
- missing notes (by ensuring the expected keys align with available notes).

### Fix option B — Add release note files for the exact audit-milestones

If the desired audit contract is that each qualified tag must correspond to a distinct `vMAJOR.MINOR[-PATCH]-release-notes.md` file, then missing entries could be resolved by adding additional release notes.

However, in this repository snapshot, the supposed missing milestones already have release-note files (e.g. `v1.0.0-release-notes.md` exists), so this option looks less consistent with the observed state.

---

## 5) Concrete recommended next step

Proceed with **gap-driven auditing**:
- Normalize tags by extracting `vMAJOR.MINOR` for milestone mapping.
- Allow mapping for tags that include qualifiers (`-kernel`, `-replay`, etc.)
- Ensure the existence check uses the same key/filename normalization convention.

Only after verifying audit behavior against the corrected normalization should code be modified.

---

## Evidence table

| Audit finding | Present in `docs/releases/`? | Likely cause |
|---|---:|---|
| Missing: `v0.1` | Yes (`v0.1-release-notes.md`) | Mapping/key mismatch |
| Missing: `v1.0.0` | Yes (`v1.0.0-release-notes.md`) | Mapping/key mismatch |
| Missing: `v1.1.0` | Yes (`v1.1.0-release-notes.md`) | Mapping/key mismatch |
| Orphaned: `v0.1.0-kernel` | N/A (qualifier) | Audit refuses mapping for qualified tags |
| Orphaned: `v0.6.0-economic-verification` | N/A (qualifier) | Audit refuses mapping for qualified tags |

---

## What this analysis does *not* change

- No documentation files were added/removed.
- No code was modified.
- No tags or commits were changed.

