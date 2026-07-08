# Slice Plan Template (Layer B — Planning artifact)

This file is the **required planning artifact** for a slice.

## Required path
A slice plan MUST exist at:

`docs/slices/vX.Y.Z/PLAN.md`

## Required lifecycle ordering (enforced by Git protocol)
1. **Create branch first**:
   - `slice/vX.Y.Z-name`
2. **Create/commit this PLAN.md next** (before any code changes)
3. **Then implement the slice work**
4. **Before opening PR**, ensure the PR diff is non-empty:
   - `git diff origin/main...HEAD --name-only` must return at least one file

## Fill-in sections

### Slice identity
- Slice branch: `slice/vX.Y.Z-name`
- Version: `vX.Y.Z`
- Purpose: *(1 sentence)*

### Context / motivation
- What problem is this slice solving?
- Why now?

### Scope (in / out)
- In scope:
  - - 
- Out of scope:
  - - 

### Planned work (checklist)
- [ ] Update docs/tests/code as needed
- [ ] Ensure audit/verification commands pass
- [ ] Confirm `git diff origin/main...HEAD --name-only` is non-empty

### Verification commands
- Unit tests:
  - `python3 -m pytest tests/... -q`
- Slice-specific scripts:
  - `python3 <path-to-script>`

### Expected outcome
- What will be true when this slice is complete?
- Which files should change?

### PR / diff sanity checks (must be done)
- [ ] `git log origin/main..HEAD --oneline` shows at least 1 commit
- [ ] `git diff origin/main...HEAD --name-only` is not empty
