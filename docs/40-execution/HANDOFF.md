# Handoff

Last updated: 2026-07-25

## Current goal

Land T-008 guided project initializer through PR review without merging
directly to `main`.

## Completed

- T-007 Signalroom merged through PR #8 with all checks passing.
- Initializer presets for core, web, mobile, full-stack, and research shapes.
- Explicit active/inactive profile and capability preview.
- External setup review list.
- Manifest-only, confirmation-gated selection behavior.
- Unit coverage for presets, incompatible selectors, and web-without-mobile.

## In progress

- T-008 branch commit, push, and PR review.

## Blockers

- None for implementation.

## Unresolved decisions

- Physical cleanup of inactive starter inventory remains deliberately separate
  from selection so initialization is reversible.

## Verification status

Eight initializer tests, five profile-engine tests, local-link validation,
showcase project checks, and full repository verification pass.

## Exact next action

Commit and push `feat/T-008-guided-project-initializer`, then open a PR titled
`feat(T-008): add guided project initializer`.

## Relevant files

- `scripts/init_project.py`
- `tests/test_initializer.py`
- `docs/60-tooling/PROFILES.md`
- `README.md`

Keep this concise enough to read in under two minutes.
