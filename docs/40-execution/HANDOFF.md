# Handoff

Last updated: 2026-08-04

## Current goal

Publish T-016's version-qualified Claude Code security guidance for human
review without enabling any credential or sandbox configuration.

## Completed

- T-009 task execution launcher merged through PR #10.
- Semantic `0.1.0` repository version and curated changelog.
- Versioned release notes and compatibility/limitations.
- Human-gated GitHub release workflow with reviewable archive/checksum.
- Clean-checkout onboarding smoke test and release contract validator.
- README quick-start visual, demo script, and launch copy.
- Public `v0.1.0` tag and release with verified archive/checksum.
- 1280×640 GitHub social-preview asset.
- Real initializer, task-planning, Signalroom interaction, UI-state, and
  verification GIFs embedded beside their README explanations.
- Adaptive greenfield, existing-brand, redesign, and restrained-baseline intake.
- Durable design brief and direction comparison artifacts with human approval.
- Stable semantic color roles and mode-aware component aliases.
- Automated theme parity and required WCAG contrast validation.
- Generated light/dark token specimen inspected at desktop and mobile widths.
- T-015 merged through PR #16 and is reconciled as done.
- Corrected the Claude Code 2.1.217/2.1.219 subagent nesting history.
- Documented the 2.1.221 credential masking and zsh permission hardening.
- Full repository verification passes for T-016.

## In progress

- T-016 is ready locally on `docs/T-016-claude-security` for commit, push, and
  draft PR creation.

## Blockers

- None for implementation or publication.

## Unresolved decisions

- Whether to add credential masking settings later. Do not do so until the
  public schema and project credential inventory are reviewed.
- Public announcements remain maintainer actions.

## Verification status

Primary-source links were checked, the prior nesting-default claim was
corrected, and full repository verification passes all ten stages, including
documentation links, security hooks, application lint, typecheck, and tests.

## Exact next action

Commit the scoped T-016 files, push `docs/T-016-claude-security`, and open a
draft PR. Human review is required. Do not self-approve or merge.

## Relevant files

- `CHANGELOG.md`
- `docs/30-engineering/SECURITY_MODEL.md`
- `docs/40-execution/PARALLELIZATION.md`
- `docs/40-execution/TASKS.jsonl`
- `docs/60-tooling/COMPATIBILITY.md`
- `docs/60-tooling/LEARNING_LEDGER.md`

Keep this concise enough to read in under two minutes.
