# GitHub workflow rules

Apply these rules to all committed project work.

## Branches

- `main` is protected integration truth.
- Do not push directly to `main` during normal work.
- Use short-lived branches named `<type>/<TASK-ID>-<slug>`.
- Use isolated worktrees for parallel agent writes.
- One owner per file or tightly coupled module during parallel work.

## Issues and tasks

- Raise or link a GitHub issue for bugs/features needing discussion, prioritization, cross-team work, durable tracking, blockers, or multi-PR delivery.
- Keep `TASKS.jsonl` as the agent-executable task graph.
- One issue may decompose into multiple task IDs.

## Pull requests

- Open a draft PR early when collaboration, dependency visibility, API/schema review, architecture review, or design feedback helps.
- PRs must link task IDs, issues when applicable, requirement IDs, acceptance criteria, and evidence.
- Do not call a task `done` before merge.
- `finish-task.sh` moves to `review`; `prepare-merge.sh` writes `done` on the task branch before final merge, while `main` remains the authoritative state.

## Review and merge

- Require passing checks and resolved blocking feedback.
- Require the appropriate security/domain/code-owner review for sensitive changes.
- Squash merge by default.
- Delete merged branches.
- Update durable state in the PR whenever project truth changes.

Full policy: `docs/70-collaboration/GITHUB_WORKFLOW.md`.
