# Handoff

Last updated: 2026-08-09

## Current goal

Replace the flat script-facing contributor experience with one discoverable
command interface without breaking existing callers or security hooks.

## Completed

- Added the root `./agentic` command interface.
- Added `.agentic/commands.json` as the command and shell-inventory source of truth.
- Grouped 23 public workflows into setup, profile, task, PR, workspace, doctor,
  token, release, and verification surfaces.
- Classified internal policy helpers, the legacy status-only task helper, and
  both runtime security hooks without exposing them as public commands.
- Kept all existing direct script paths compatible.
- Migrated primary contributor, installation, collaboration, and release docs
  to the unified interface.
- Added registry completeness, help, JSON discovery, safety-boundary, and exact
  argument-forwarding tests.

## Blockers

- None.

## Unresolved decisions

- A second maintainer is still needed before requiring a non-zero GitHub
  approval count. The finalizer does not substitute for independent review.
- The existing runtime-baseline warnings remain advisory and unrelated to PR
  command routing.
- Legacy script removal requires a later release-backed deprecation decision;
  this task deliberately performs no bulk deletion or relocation.

## Verification status

- Eight command-interface tests pass.
- All 30 shell files are classified exactly once.
- Full repository verification passes across 26 tracked tasks, local links,
  security hooks, runtime/Codex policy, design tokens, and Showcase checks.

## Exact next action

Use `./agentic --help` as the normal entry point. Whenever a shell file is
added, renamed, or removed, update `.agentic/commands.json` in the same change
and keep the registry completeness tests passing.

## Relevant files

- `agentic`
- `.agentic/commands.json`
- `scripts/agentic_cli.py`
- `scripts/README.md`
- `tests/test_agentic_cli.py`
- `CLAUDE.md`
- `CONTRIBUTING.md`

Keep this concise enough to read in under two minutes.
