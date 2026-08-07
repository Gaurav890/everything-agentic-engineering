# Handoff

Last updated: 2026-08-07

## Current goal

Reconcile T-021's durable task state after approved PR #22 merged before its
final bookkeeping commit, without changing implementation or authority.

## Completed

- Added trusted-project Codex configuration with bounded instruction context
  and concurrent spawned-agent threads.
- Exposed one canonical local skill catalog to Claude, Codex repository
  discovery, and skills-only plugin packaging.
- Added the validated `codex-adapter` skill and plugin manifest.
- Wired Codex lifecycle hooks to the reviewed destructive-command and
  post-edit secret-scan scripts.
- Extended secret scanning to Codex `apply_patch` payloads.
- Added multi-terminal and Codex worktree guidance, including ownership,
  dependency, integration, and shared-ledger rules.
- Added a dependency-free doctor and six Codex adapter tests.
- Official skill and plugin validators pass.
- Full repository verification passes after restoring locked worktree
  dependencies.
- PR #22 received human approval and merged into `main`.

## In progress

- A documentation-only follow-up PR to record T-021 as `done` on authoritative
  `main`.

## Blockers

- None for publication.

## Unresolved decisions

- The installed local Codex reports 0.146.0 and is below the documented 0.147.0
  plugin baseline. The adapter warns by default and fails only in explicit
  strict-runtime mode. Runtime upgrade remains a human decision.
- Codex-specific subagent role adapters remain a separate future task.
- Plugin marketplace publication and installation policy remain separate
  reviewed release actions.

## Verification status

- `codex-adapter` skill validation: pass.
- Plugin schema validation: pass.
- Default doctor: pass with the expected runtime warning.
- Strict runtime doctor: correctly rejects the older installed runtime.
- Security-hook and adapter unit tests: pass.
- `./scripts/verify.sh full`: pass.

## Exact next action

Confirm the follow-up PR's GitHub checks. If they are green, a human may
squash-merge it and delete its branch. Never self-approve or self-merge.

## Relevant files

- `AGENTS.md`
- `.codex/`
- `.codex-plugin/plugin.json`
- `.agents/skills`
- `.claude/skills/codex-adapter/`
- `docs/60-tooling/CODEX.md`
- `docs/70-collaboration/PARALLEL_TERMINALS.md`
- `scripts/codex-doctor.sh`
- `tests/test_codex_adapter.py`

Keep this concise enough to read in under two minutes.
