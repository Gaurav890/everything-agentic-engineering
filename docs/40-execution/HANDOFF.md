# Handoff

Last updated: 2026-08-10

## Current goal

Keep the human-approved PR finalization path resumable without weakening its
ledger-only mutation boundary or human-only merge authority.

## Completed

- The finalizer recognizes only its exact uncommitted or staged task-ledger
  `review` to `done` transition as a recoverable dirty state.
- Recovered ledger state is fully reverified before staging and commit.
- Unrelated files, extra ledger edits, unsupported Git states, and invalid PR
  contracts still stop before GitHub mutation.
- GitHub check registration is polled for a bounded 55 seconds before a clear,
  safely resumable timeout is reported.
- Already-committed, pushed, and ready checkpoints remain idempotent.
- Documentation consistently tells maintainers to rerun the same finalizer
  rather than manually editing `TASKS.jsonl`.

## Blockers

- None.

## Unresolved decisions

- A second maintainer is still needed before requiring a non-zero GitHub
  approval count. The finalizer does not substitute for independent review.
- Check-registration polling confirms that GitHub created a run; existing
  branch protection remains the authority for which checks are required.
- Runtime-baseline warnings remain advisory and unrelated to PR finalization.

## Verification status

- Twelve finalization tests pass, including staged and unstaged recovery,
  unsafe-ledger rejection, delayed check registration, timeout guidance,
  idempotent ready-state recovery, and no approval or merge commands.
- Full repository verification passes across 27 tracked tasks, local links,
  security hooks, runtime/Codex policy, design tokens, and Showcase checks.

## Exact next action

After direct human approval of a reviewed task, run
`./agentic pr finalize T-### --yes`. If it is interrupted at a supported
checkpoint, rerun that same command. A human still performs the squash merge
only after required checks pass.

## Relevant files

- `scripts/finalize_pr.py`
- `tests/test_pr_finalization.py`
- `docs/70-collaboration/PR_FINALIZATION.md`
- `docs/70-collaboration/GITHUB_WORKFLOW.md`
- `CLAUDE.md`
- `AGENTS.md`

Keep this concise enough to read in under two minutes.
