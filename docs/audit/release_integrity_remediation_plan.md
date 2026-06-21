# Release Integrity Remediation Plan (v1.1.1 Slice 1)

Goal: Make `python3 scripts/audit/release_integrity_audit.py` return:
- `audit_valid: true`
- `integrity_score: 1.0`

Also ensure:
- `python3 -m pytest tests/audit/test_release_integrity.py -q` still passes.

This plan is based on:
- `docs/audit/release_integrity_report.json`
- `docs/audit/release_integrity_gap_analysis.md`
- `scripts/audit/release_integrity_audit.py`

---

## Current state

Unit tests pass (determinism + API contract), but the audit CLI reports `audit_valid: false` because it currently:
1. Computes expected release-note milestones from tags in a way that does not reconcile with how release notes are keyed.
2. Treats qualified tags (e.g. `v0.1.0-kernel`) as “orphaned” because mapping is currently too strict.

The audit reports:
- `missing_release_notes`: includes milestones like `v0.1`, `v1.0.0`, … `v1.1.0`.
- `orphaned_tags`: includes qualified tags with suffixes like `-kernel`, `-replay`, `-sync-ops-finalization`, etc.

---

## What Sixth should verify next (evidence-driven)

For each entry in `missing_release_notes` and `orphaned_tags`, Sixth should:
1. Show the exact tag string.
2. Show the expected release-note path as the audit computes it.
3. Check filesystem existence of that expected path.
4. Identify the exact normalization mismatch (tag→milestone key and/or key→filename mapping).

This is to confirm whether the fix should be:
- (A) normalization (tag parsing / milestone key derivation)
- (B) release-note key extraction/discovery
- (C) both

---

## Remediation options (choose minimum changes)

### Option A (Recommended): Normalize tags with qualifiers to milestone versions

Change the mapping logic so qualified tags contribute to the corresponding milestone release note:
- `v0.1.0-kernel` → expected milestone `v0.1` (thereby checking `docs/releases/v0.1-release-notes.md`)
- `v0.2.0-replay` → expected milestone `v0.2`
- `v0.6.0-economic-verification` → expected milestone `v0.6`

This resolves orphaned qualified tags.

Implementation idea:
- Introduce a `normalize_tag_to_version_prefix(tag) -> "vMAJOR.MINOR"` helper.
- In `_find_matching_note(tag)` call normalization first, then compute expected filename from `vMAJOR.MINOR`.

### Option B: Fix the milestone key extraction & presence check

Ensure that the internal `available_notes` keys and the key used in the existence check are consistent.

The audit currently builds `available_notes` from:
- filename like `docs/releases/v0.1-release-notes.md`
- extracting key `v0.1`

But the CLI reports `missing_release_notes` entries like `v1.0.0`.

That suggests that the audit is sometimes deriving a different milestone key than the one extracted from filenames.

Implementation idea:
- Decide on a single canonical milestone key shape:
  - either `vMAJOR.MINOR` (e.g. `v1.0`)
  - or `vMAJOR.MINOR.PATCH` (e.g. `v1.0.0`)
- Update mapping and discovery to always use that same shape.

Given the existing filenames in `docs/releases/`, the repo contains both:
- `v0.1-release-notes.md` (no patch)
- `v1.0.0-release-notes.md` (includes patch)

So the remediation likely requires: when a tag has patch information, prefer the patch-shaped milestone filename.

Implementation idea:
- If tag contains `vX.Y.Z` pattern, then expected note is `vX.Y.Z-release-notes.md`.
- Otherwise, expected note is `vX.Y-release-notes.md`.

---

## Minimal mapping contract the audit should implement

For a tag `vA.B` / `vA.B.*`:
- If tag indicates patch (`vA.B.C` exists in the tag before any `-qualifier`), expect `docs/releases/vA.B.C-release-notes.md`.
- Else expect `docs/releases/vA.B-release-notes.md`.

Qualified tags simply affect suffix stripping; they should not change which milestone release note is targeted.

---

## Concrete code changes (minimum)

1. Modify `_find_matching_note(tag)`:
   - Parse tag as:
     - version prefix (vA.B) and optional patch C
     - optional qualifier (-...)
   - If patch exists in the tag’s version portion: return `vA.B.C-release-notes.md`
   - Else: return `vA.B-release-notes.md`

2. Modify (or wrap) `expected_release_note_filename(...)` to match the above contract.

3. Ensure `collect_release_notes()` key derivation matches the above contract.
   - If note file is `vA.B-release-notes.md`, key is `vA.B`.
   - If note file is `vA.B.C-release-notes.md`, key is `vA.B.C`.

4. Update `run_audit()` scoring logic remains the same, but now should yield:
   - `tags_checked == tags_valid`
   - `missing_release_notes == []`
   - therefore `audit_valid == true`
   - since determinism tests already pass, keep sorting behavior.

---

## Documentation files required

No additional docs required if the above remediation makes `audit_valid: true`.

If after remediation `audit_valid` is still false, append a short factual update to:
- `docs/audit/release_integrity_gap_analysis.md`

---

## Tests to re-run after minimal changes

1. `python3 -m pytest tests/audit/test_release_integrity.py -q`
2. `python3 scripts/audit/release_integrity_audit.py`
   - confirm output includes:
     - `Audit valid: True`
     - `Integrity score: 1.0`

---

## Acceptance criteria for Slice 1 completion

- `python3 scripts/audit/release_integrity_audit.py` returns exit code 0.
- `docs/audit/release_integrity_report.json` contains:
  - `audit_valid: true`
  - `integrity_score: 1.0`
- Unit tests still pass.



