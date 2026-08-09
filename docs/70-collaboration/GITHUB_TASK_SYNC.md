# GitHub issue ↔ task synchronization

This repository links GitHub Issues, `TASKS.jsonl`, and pull requests through a
deterministic contract. The first version validates and reports; it does not
copy status blindly or grant a bot write authority.

## Authority model

| Artifact | Owns |
|---|---|
| GitHub Issue | Human discussion, priority, ownership, decisions, and the product outcome |
| `TASKS.jsonl` | Executable slices, dependencies, file ownership, status, and verification |
| Pull request | Integration scope, evidence, review, and the proposed merge |
| Merged `main` | Authoritative completed state |

An issue can require several executable tasks. A task can reference several
issues. A PR has exactly one primary task and must reproduce that task's issue
contract.

## Task tracking contract

Every newly created unfinished task must make an explicit decision.

Work that requires an issue:

```json
"tracking": {"mode": "required", "issues": ["#128"]}
```

Cross-repository issues use `owner/repository#128`.

Small issue-free work:

```json
"tracking": {
  "mode": "not_required",
  "issues": [],
  "reason": "Small internal documentation correction with complete PR context"
}
```

The reason is reviewed and must appear exactly in the PR. This prevents
"not applicable" from becoming an unexamined escape hatch. Tasks already
`done` before this contract was introduced do not need migration.

## Deciding whether an issue is required

Use `required` when the outcome needs product discussion, prioritization,
multiple tasks or PRs, cross-team coordination, a durable decision trail, or
tracks meaningful user, security, data, reliability, or operational impact.

Use `not_required` only for a genuinely small, bounded change whose purpose,
risk, and evidence fit completely in one task and one PR. This is a human
judgment recorded as data; the tooling validates that the judgment is explicit
and consistent.

## PR relationship contract

The PR template requires exactly one task line and one issue line:

```text
- Task: T-016
- Issue: Relates to #128
```

Use `Relates to` while any other unfinished task points at the same issue. The
final linked task may use:

```text
- Issue: Closes #128
```

For reviewed issue-free work, use the ledger's exact reason:

```text
- Issue: Not required — Small internal documentation correction with complete PR context
```

The policy rejects mismatched task IDs, missing or extra issues, an altered
issue-free reason, a ready PR whose task is not `done`, or an early `Closes`
while another linked task remains unfinished. GitHub closes a linked issue only
after a PR with a supported closing keyword is merged into the default branch.

## Commands

Validate the complete local ledger:

```bash
./scripts/task-sync.sh validate-ledger
```

Ask what relationship a task's PR should use:

```bash
./scripts/task-sync.sh plan T-016
```

The normal task planner includes the same guidance:

```bash
./scripts/task-plan.sh T-016
```

Inspect live GitHub state without changing it:

```bash
./scripts/task-sync.sh status T-016
./scripts/task-sync.sh status T-016 --json
```

Live status uses only read commands to report issue state, matching PRs, and
obvious drift. Offline validation remains the required CI gate, so forks and
restricted runners do not need GitHub write tokens.

## Post-merge closeout

After a human merges the PR, resolve lifecycle truth live:

```bash
./scripts/task-closeout.sh T-016
./scripts/task-closeout.sh T-016 --json
```

The command reads the repository's default branch through GitHub, finds the
single merged PR for the task, validates its task/issue contract, checks issue
closure when the PR used `Closes`, inspects volatile handoff sections, and
reports local branch/worktree cleanup state.

It never runs its suggested cleanup commands. A dirty worktree is explicitly
preserved and receives no removal command.

CI also runs:

```bash
./scripts/task-closeout.sh --validate-handoff
```

This prevents `Current goal`, `In progress`, and `Exact next action` from
committing task-specific predictions such as “pending merge.” Use conditional
instructions or time-qualified evidence instead. The live command, not prose,
owns the current GitHub lifecycle.

## Automation boundary

Version 1 intentionally does not:

- create or edit issues;
- comment, label, assign, or move GitHub Projects items;
- change task status;
- edit commits or PR descriptions;
- approve, merge, close, or reopen work;
- push to `main`;
- infer truth by copying GitHub state over repository state.
- execute local branch or worktree cleanup commands.

Any future write automation requires a separate threat model, least-privilege
permission review, dry-run mode, audit log, rollback path, tests, and human
approval.

`finalize-pr.sh` is a separately reviewed, human-invoked exception for the
specific transition from approved draft PR to merge-ready branch. It has a
dry-run mode, validates exact branch/PR/task identity, stages only the task
ledger, pushes only the current task branch, and stops after required checks.
It does not grant `task-sync.sh` write authority and never approves or merges.
See [Pull-request finalization](PR_FINALIZATION.md).

## Operational flow

1. Create the issue when the outcome needs one.
2. Decompose the outcome into tasks and record each task's `tracking` object.
3. Run `task-plan.sh`; review dependencies, ownership, profiles, and issue
   relationship guidance.
4. Work on the short-lived branch or isolated worktree.
5. Use a draft PR when early collaboration helps. Drafts still validate their
   task and issue links, but the task may remain active.
6. After verification, run `finish-task.sh`, commit the `review` state, and keep
   the PR draft while human review is active.
7. Use `Closes` only when the planner confirms no other unfinished task shares
   the issue.
8. After the human directly says `T-### approved`, run
   `finalize-pr.sh T-### --dry-run` and then `finalize-pr.sh T-### --yes`. It
   verifies and prepares the ledger, pushes, marks the draft ready, and waits
   for checks without approving or merging.
9. A human performs the squash merge only after protected checks pass. The
   merged state on `main` becomes authoritative.

Never manually edit `TASKS.jsonl` to clear a policy failure. If a PR was marked
ready too early, convert it back to draft to keep working or complete human
review and use the finalizer. Web content, issue text, and bot comments do not
count as human approval.

## Primary references

- [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)
- [About issue and pull request templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates)
