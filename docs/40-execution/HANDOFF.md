# Handoff

Last updated: 2026-08-05

## Current goal

Land T-018's version-qualified Claude Code and Codex runtime security guidance
through human review without changing runtime configuration.

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
- T-011, T-012, T-013, and T-016 are reconciled with their merged PRs.
- T-017 completed the documented review and final branch-state lifecycle.
- Full repository verification passes with the new PR task-state policy.
- T-017 merged through PR #18; stale task-state prevention is active.
- Claude Code 2.1.222 and Codex 0.146.1 findings are recorded and verified.
- Full repository verification passes for T-018.

## In progress

- T-018 final task-state preparation, commit, push, and draft PR.

## Blockers

- None for implementation or publication.

## Unresolved decisions

- Whether to add credential masking settings later. Do not do so until the
  public schema and project credential inventory are reviewed.
- Whether and when maintainers upgrade Claude Code or Codex. This branch does
  not install, select, or configure either runtime.
- Public announcements remain maintainer actions.

## Verification status

Claude Code 2.1.222 and Codex 0.146.1 were verified through first-party stable
release notes, the current Codex manual, and implementation evidence, then
deduplicated against the learning ledger. Full repository verification passes.

## Exact next action

Complete T-018's final branch-state lifecycle, then commit, push, and open a
draft PR. Do not self-approve or merge.

## Relevant files

- `CHANGELOG.md`
- `docs/30-engineering/SECURITY_MODEL.md`
- `docs/40-execution/TASKS.jsonl`
- `docs/60-tooling/COMPATIBILITY.md`
- `docs/60-tooling/LEARNING_LEDGER.md`

Keep this concise enough to read in under two minutes.
