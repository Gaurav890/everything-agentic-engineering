# Task execution launcher

The task launcher turns `TASKS.jsonl` into a safe, reviewable workspace plan.
It prepares work; it does not implement, merge, deploy, install, or bypass
approval.

## Plan first

```bash
./scripts/task-plan.sh T-009
./scripts/task-plan.sh T-009 --json
```

The plan reports:

- requirement and acceptance-criteria IDs;
- the reviewed GitHub issue contract and whether the PR should relate or close;
- dependency state;
- recommended specialist agent;
- compatibility with active project profiles;
- exclusive file ownership and collisions;
- verification gates;
- active parallel work;
- branch or worktree recommendation;
- blockers and the exact reviewed start command.

Planning is read-only.

## Start after review

```bash
./scripts/task-start.sh T-009 --yes
```

The launcher derives a kebab-case slug and chooses:

- a short-lived branch when no other independent task is active;
- an isolated worktree when parallel work already exists.

Override only when the plan justifies it:

```bash
./scripts/task-start.sh T-009 \
  --slug task-execution-launcher \
  --mode worktree \
  --type feat \
  --base main \
  --yes
```

Without `--yes`, no branch, worktree, or task state changes.

## Fail-closed gates

Starting is blocked when:

- the task does not exist;
- its status is already `in_progress`, `review`, or `done`;
- a dependency is missing or not `done`;
- a required project profile is inactive;
- another active task owns overlapping files;
- the working tree is dirty;
- the requested slug or branch type is invalid.
- any unfinished task lacks a valid issue link or reviewed issue-free reason.

Execution-ledger files under `docs/40-execution/` are shared coordination state
and do not create false file-ownership collisions. Product and implementation
files remain exclusive.

## Profile routing

The launcher infers required profiles from task ownership, file scope, and
verification:

| Signal | Required profile |
|---|---|
| Frontend owner or `apps/web` / `apps/showcase` | `web-next` |
| Mobile owner or `apps/mobile` | `mobile-expo` |
| Research owner or research verification | `research-enabled` |
| Backend owner | `backend-supabase` or `backend-convex` |
| Design files, visual QA, design critique, accessibility | `design-critical` |

The project manifest remains authoritative. The launcher does not activate a
missing profile automatically; use the profile preview workflow first.

## GitHub tracking

The launcher includes the deterministic issue/task plan. Inspect the same
contract directly with:

```bash
./scripts/task-sync.sh validate-ledger
./scripts/task-sync.sh plan T-009
./scripts/task-sync.sh status T-009
```

`status` is an optional read-only live inspection. CI uses offline ledger and
PR-payload validation and does not need GitHub write authority. See
[`GITHUB_TASK_SYNC.md`](GITHUB_TASK_SYNC.md).
