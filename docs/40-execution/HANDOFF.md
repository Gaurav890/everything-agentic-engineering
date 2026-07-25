# Handoff

Last updated: 2026-07-25

## Current goal

Land the T-010 `v0.1.0` release package through review without publishing or
merging directly to `main`.

## Completed

- T-009 task execution launcher merged through PR #10.
- Semantic `0.1.0` repository version and curated changelog.
- Versioned release notes and compatibility/limitations.
- Human-gated GitHub release workflow with reviewable archive/checksum.
- Clean-checkout onboarding smoke test and release contract validator.
- README quick-start visual, demo script, and launch copy.

## In progress

- T-010 PR #11 checks and review.

## Blockers

- None for implementation.

## Unresolved decisions

- Final recording, social preview, GitHub topics, tag, public release, and
  announcements remain maintainer actions after merge.

## Verification status

Release contract validation, clean-checkout onboarding smoke test, full
repository verification, documentation-link validation, token/profile/task
tests, security-hook tests, and showcase project checks pass locally.

## Exact next action

Wait for PR #11 checks, review the release claims and publish gate, then squash
merge if all required checks pass. Do not publish `v0.1.0` as part of the merge.

## Relevant files

- `.github/workflows/release.yml`
- `scripts/release-check.sh`
- `scripts/release-smoke-test.sh`
- `docs/releases/v0.1.0.md`
- `docs/70-collaboration/RELEASING.md`
- `docs/80-showcase/DEMO_SCRIPT.md`
- `README.md`

Keep this concise enough to read in under two minutes.
