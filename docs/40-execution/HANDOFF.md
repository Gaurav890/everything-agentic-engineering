# Handoff

Last updated: 2026-08-07

## Current goal

Land T-022's safe Codex specialist-role pack through human review without
expanding models, providers, MCPs, credentials, network access, writable
sandboxes, or approval policy.

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
- PRs #22 and #23 merged; T-021 is `done` on authoritative `main`.
- GitHub `main` protection now requires `verify` and `policy`, applies to
  administrators, requires resolved conversations and linear history, and
  blocks force pushes and deletion.
- Clean merged T-021 worktrees and branches were removed.
- Added seven project-scoped, read-only Codex specialist roles and a
  dependency-free validator that rejects unreviewed configuration fields.
- Updated the cross-runtime routing, Codex guide, parallel-worktree contract,
  tests, README, and durable state.

## In progress

- Draft PR preparation for `feat/T-022-codex-specialist-roles`.

## Blockers

- None for publication.

## Unresolved decisions

- The installed local Codex reports 0.146.0 and is below the documented 0.147.0
  plugin baseline. The adapter warns by default and fails only in explicit
  strict-runtime mode. Runtime upgrade remains a human decision.
- A second maintainer is needed before enabling a non-zero required approval
  count without blocking the solo-maintainer workflow.
- Plugin marketplace publication and installation policy remain separate
  reviewed release actions.

## Verification status

- `codex-adapter` skill validation: pass.
- Plugin schema validation: pass.
- Default doctor: pass with the expected runtime warning.
- Strict runtime doctor: correctly rejects the older installed runtime.
- Security-hook and adapter unit tests: pass.
- `./scripts/verify.sh full`: pass.
- Seven-role restricted schema validation: pass.
- Nine Codex adapter tests: pass.
- Codex adapter skill and repository plugin validation: pass.
- T-022 `./scripts/verify.sh full`: pass.

## Exact next action

Commit and push the reviewed T-022 scope, then open a draft PR. Never
self-approve or self-merge.

## Relevant files

- `AGENTS.md`
- `.codex/`
- `.codex/agents/`
- `.codex-plugin/plugin.json`
- `.agents/skills`
- `.claude/skills/codex-adapter/`
- `docs/60-tooling/CODEX.md`
- `docs/70-collaboration/PARALLEL_TERMINALS.md`
- `scripts/codex-doctor.sh`
- `tests/test_codex_adapter.py`

Keep this concise enough to read in under two minutes.
