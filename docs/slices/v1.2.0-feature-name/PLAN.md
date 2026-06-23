# Slice Plan (Layer B — Planning artifact) — v1.2.0

## Required path
`docs/slices/v1.2.0-feature-name/PLAN.md`

## Slice identity
- Slice branch: `slice/v1.2.0-feature-name`
- Version: `v1.2.0`
- Purpose: *(describe in one sentence what this slice accomplishes)*

## Context / motivation
*(why this slice is needed; link to issues/audits/docs if applicable)*

## Scope (in / out)
### In scope
- [ ] *(list planned changes)*
- [ ] *(update docs/tests/code as needed)*
- [ ] Ensure verification commands pass

### Out of scope
- [ ] *(explicitly list what you will not do in this slice)*

## Planned work (checklist)
- [ ] Create/update `docs/audit/...` or other required docs
- [ ] Run critical-path verification
- [ ] Confirm `git diff origin/main...HEAD --name-only` is non-empty

## Verification commands
- `python3 -m pytest tests/audit/test_release_integrity.py -q`
- `python3 scripts/audit/release_integrity_audit.py`

## Expected outcome
- *(what must be true when done, e.g. audit_valid/integrity_score/tests passing)*

## PR / diff sanity checks (must be done)
- [ ] `git log origin/main..HEAD --oneline` shows at least 1 commit
- [ ] `git diff origin/main...HEAD --name-only` is not empty
