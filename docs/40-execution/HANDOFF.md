# Handoff

Last updated: 2026-08-09

## Current goal

Keep the review-to-merge experience human-friendly without weakening task,
verification, protected-branch, or human-merge controls.

## Completed

- Added a dry-run-capable, human-invoked PR finalizer.
- Reused the existing full verification and low-level prepare gate.
- Limited automated staging and commit scope to `TASKS.jsonl`.
- Added recovery for a PR that was marked ready before finalization.
- Replaced manual-ledger guidance with the direct `T-### approved` interaction.
- Documented the finalizer's authority boundary and failure recovery.
- Added deterministic finalizer and PR-policy tests.
- Full repository verification passes across all ten stages.

## Blockers

- None.

## Unresolved decisions

- A second maintainer is still needed before requiring a non-zero GitHub
  approval count. The finalizer does not substitute for independent review.
- The existing runtime-baseline warnings remain advisory and unrelated to PR
  finalization.

## Verification status

- Six PR-finalization tests pass.
- Twelve GitHub task-sync tests pass.
- All 25 task records pass the tracking contract.
- Local documentation links and shell/Python validation pass.
- Showcase lint, typecheck, and model tests pass.
- Full repository verification passes.

## Exact next action

For any task under review, keep its PR draft until a human directly approves
the named task. Then preview and run `finalize-pr.sh`; merge separately only
after required checks pass. After merge, use `task-closeout.sh`.

## Relevant files

- `scripts/finalize_pr.py`
- `scripts/finalize-pr.sh`
- `tests/test_pr_finalization.py`
- `scripts/github_task_sync.py`
- `docs/70-collaboration/PR_FINALIZATION.md`
- `docs/70-collaboration/GITHUB_WORKFLOW.md`

Keep this concise enough to read in under two minutes.
