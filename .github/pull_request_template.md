## Problem

What user problem or failure does this change address?

## Approach

What changed, and why is this the smallest safe solution?

## Evidence and risks

Which official documentation, project data, or reproducible test supports the
change? What could go wrong?

## Verification

- [ ] `python3 scripts/test_operator.py`
- [ ] `python3 scripts/validate_skill.py .`
- [ ] No credentials, private paths, raw project data, or generated caches
- [ ] README and changelog updated when public behavior changed
- [ ] External mutations remain approval-gated and dry-run-first
