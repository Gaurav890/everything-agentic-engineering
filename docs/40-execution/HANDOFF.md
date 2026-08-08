# Handoff

Last updated: 2026-08-07

## Current goal

Use `task-closeout.sh T-024` as the live lifecycle source. When it reports a
clean closeout, select the connected Signalroom vertical slice as the next
bounded product task.

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
- PR #24 passed the protected `verify` and `policy` checks and merged into
  `main` as `7906e62`; T-022 is now durably `done`.
- Removed the clean merged T-022 worktree and local feature branch. The merged
  work remains recoverable through PR #24 and its Git history.
- T-023 landed through PR #27 as `2dc1b63`; issue #26 closed automatically and
  both protected checks passed.
- T-023 established deterministic Issue ↔ task ↔ PR validation and read-only
  live drift reporting.

## In progress

- Lifecycle state is intentionally not duplicated here. Run the closeout
  command named in the current goal for authoritative GitHub and `main` truth.

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
- T-022 `./scripts/prepare-merge.sh T-022`: pass.
- PR #24 required `verify` and `policy` checks: pass.
- T-022 task state on authoritative `main`: `done`.
- T-023 synchronization tests: 12 pass.
- T-023 task-planner tests: 11 pass.
- T-023 ledger validation: 22 tasks valid.
- T-023 post-merge state: PR #27 merged, issue #26 closed, task `done` on
  authoritative `main`.
- T-024 closeout tests: 12 pass.
- T-024 handoff lifecycle guard: pass.
- T-024 task tracking ledger: 23 tasks valid.
- T-024 `./scripts/verify.sh full`: pass.
- T-023 `./scripts/verify.sh full`: pass.

## Exact next action

Run the closeout command named above. Address reported findings through a new
task branch; never rewrite durable state or delete local work automatically.
When the report passes, choose the next bounded task from the roadmap.

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
- `docs/70-collaboration/GITHUB_TASK_SYNC.md`
- `scripts/github_task_sync.py`
- `tests/test_github_task_sync.py`
- `scripts/post_merge_closeout.py`
- `scripts/task-closeout.sh`
- `tests/test_post_merge_closeout.py`

Keep this concise enough to read in under two minutes.
