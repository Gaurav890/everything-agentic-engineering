# Handoff

Last updated: 2026-08-09

## Current goal

Keep runtime compatibility deterministic and visible while preserving every
optional capability and actual tool upgrade as an explicit human decision.

## Completed

- T-024 closeout passed against authoritative `main`: task `done`, issue #28
  closed, no transient handoff claims, and exact clean local cleanup identified.
- Removed only the clean merged T-024 local worktree and branch.
- Issue #30 now owns the T-025 human discussion.
- Added one versioned Claude Code and Codex runtime policy.
- Added advisory, strict, runtime-specific, and JSON doctor modes.
- Reused the shared Codex version policy from `codex-doctor.sh`.
- Added optional capability gates for self-hosted and cross-session Claude
  execution, archive plugin sources, Codex plugins, MCP 2026-07-28, and
  automatically reviewed approvals.
- Added deterministic policy, version, JSON, and fail-closed tests.
- Restored the exact locked dependency set offline with zero downloads.
- Full repository verification passes across all ten stages.
- Maintainer inspection completed and the final preparation gate passed.

## In progress

- No implementation work remains; the prepared checkpoint awaits protected
  checks and maintainer-controlled integration.

## Blockers

- None.

## Unresolved decisions

- The inspected developer environment remains below both recommended runtime
  baselines. An actual tool upgrade is a separate human-owned action.
- Optional runtime surfaces require separate threat models and pilots; this
  task intentionally enables none of them.
- A second maintainer is still needed before requiring a non-zero approval
  count in the solo-maintainer repository.

## Verification status

- Seven runtime compatibility tests pass.
- Ten Codex adapter tests pass.
- Advisory reporting correctly identifies Claude Code 2.1.220 and Codex
  0.146.0 prerelease as below baseline without mutation.
- Simulated strict validation rejects old versions and accepts Claude Code
  2.1.225 plus Codex 0.147.0.
- JSON output parses and declares `mutation_performed: false`.
- All 24 task records pass the GitHub tracking contract.
- Showcase lint, typecheck, and model tests pass.
- Full repository verification passes after the task moved to `review`.
- The final preparation gate passed after human inspection.

## Exact next action

After the protected checks pass, use the documented squash strategy. Treat any
runtime upgrade or optional capability activation as separate approved work.

## Relevant files

- `.agentic/runtime-baselines.json`
- `scripts/runtime_doctor.py`
- `scripts/runtime-doctor.sh`
- `scripts/codex-doctor.sh`
- `tests/test_runtime_compatibility.py`
- `tests/test_codex_adapter.py`
- `docs/60-tooling/COMPATIBILITY.md`
- `docs/30-engineering/SECURITY_MODEL.md`

Keep this concise enough to read in under two minutes.
