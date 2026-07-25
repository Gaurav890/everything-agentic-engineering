# Handoff

Last updated: 2026-07-25

## Current goal

Land T-005 profile-engine changes through review without merging directly to
`main`.

## Completed

- Machine-readable project/profile/resource configuration.
- Deterministic dependency and conflict resolution.
- Profile doctor and non-destructive preview/select commands.
- Resolution, conflict, confirmation, isolated write, and full verification.

## In progress

- Final commit, push, and pull-request review.

## Blockers

- None for implementation. GitHub PR creation may still require the direct web
  URL because the connected integration has previously returned 403.

## Unresolved decisions

- Future versions may add reviewed installers or cleanup execution. Version one
  intentionally reports and previews only.

## Verification status

Full repository verification and profile-engine scenario tests pass.

## Exact next action

Commit and push `feat/T-005-profile-engine`, then open a PR titled
`feat(T-005): add deterministic project profile engine`.

## Relevant files

- `.agentic/project.json`
- `.agentic/profiles/`
- `.agentic/resources.json`
- `scripts/profile_engine.py`
- `docs/60-tooling/PROFILES.md`

Keep this concise enough to read in under two minutes.
