# Parallel terminals and Codex worktrees

Use parallel terminals only when the task graph contains independent outputs.
The objective is concurrent progress with explicit ownership, not the maximum
number of active agents.

## Required plan

Before opening write-capable workspaces, record:

1. Dependency DAG.
2. One owner per task.
3. Exclusive file or tightly coupled module ownership.
4. Shared contracts and their merge order.
5. Per-task verification.
6. Final integration and evaluator gates.

Use:

```bash
./scripts/task-plan.sh T-101
```

Planning is read-only. Fix missing dependencies, inactive profiles, or file
collisions before creating a branch.

## Recommended terminal topology

```text
Terminal 0 — orchestrator and integration state
    ├── Terminal 1 — architecture or shared contract
    ├── Terminal 2 — backend implementation
    ├── Terminal 3 — web implementation
    └── Terminal 4 — read-only QA/security evaluation
```

Do not open dependent implementation work until the contract it consumes is
stable enough to branch from or has merged.

## Repository-managed worktrees

After each task exists in `TASKS.jsonl` and passes planning:

```bash
./scripts/task-start.sh T-101 --mode worktree --yes
./scripts/task-start.sh T-102 --mode worktree --yes
./scripts/task-start.sh T-103 --mode worktree --yes
```

The launcher prints each worktree path. Open each path in a separate terminal
and start Codex there. Never check out the same branch in two worktrees.

## Subagents versus worktree workers

Use in-session Codex subagents for bounded read-only work that benefits from a
separate context window:

- architecture mapping;
- product and requirements analysis;
- primary-source research;
- design critique;
- security review;
- test and acceptance analysis;
- final integration review.

The project roles under `.codex/agents/` enforce that read-only default. They
share the parent turn's approved capabilities but do not add model, MCP,
network, credential, or approval configuration.

Use a separate task branch and worktree for every parallel worker that must
edit code or durable documentation. A custom role is context isolation; it is
not Git isolation. Never let several writable subagents race inside one
checkout.

The lower-level command remains available when the reviewed plan requires an
explicit branch type or base:

```bash
./scripts/create-worktree.sh T-102 enterprise-auth feat main
```

## Codex desktop worktrees

In Codex desktop:

1. Start a new task with **Worktree** selected.
2. Choose the reviewed base branch.
3. Give the task its task ID, owned files, acceptance criteria, and checks.
4. Use **Create branch here** when the result is ready to commit and publish.
5. Use **Handoff** when local foreground inspection is required.

Codex-managed worktrees may begin at detached HEAD. A branch can be checked
out in only one worktree at a time.

## Feature and technical-spec routing

Parallelize a technical specification when its artifact is independent:

| Work | Parallel-safe example | Sequential example |
|---|---|---|
| Architecture | Separate ADRs for unrelated services | Two writers changing one API contract |
| Backend | Independent bounded contexts | Schema migration before its data access layer |
| Frontend | Separate routes consuming a stable API | UI built against an undecided contract |
| Mobile | Native client after shared domain types stabilize | Concurrent edits to shared generated types |
| Evaluation | Read-only threat model and test analysis | Final integration certification before merge |

Foundational merge order normally remains:

```text
architecture/schema/types
→ backend/API
→ web/mobile consumers
→ integration fixes
→ independent QA/security evaluation
```

Change the order only when the recorded dependency graph justifies it.

## Shared coordination state

`TASKS.jsonl`, `CURRENT_STATE.md`, `PROGRESS.md`, and `HANDOFF.md` are shared
coordination artifacts. Give their final integration edits to the orchestrator.
Workers should return evidence and proposed state changes rather than racing to
rewrite the same ledger lines.

The current task launcher ignores execution-ledger paths for ownership
collision detection, but Git can still produce textual conflicts. Treat the
orchestrator as the single integration writer for those files.

## Local environment and secrets

Do not copy `.env` files into every worktree automatically. When an approved
local workflow genuinely requires ignored setup files, use Codex's local
`.worktreeinclude` mechanism deliberately and keep the file list minimal.
Never commit secrets or production credentials.

## Completion

Each worker returns:

```text
Outcome
Scope
Files changed
Verification evidence
Risks
Exact handoff
```

Then the orchestrator:

1. Integrates in dependency order.
2. Updates dependent branches from the new base.
3. Runs cross-layer verification.
4. Obtains independent review.
5. Updates durable execution state.
6. Opens or updates the PR without merging it.

Remove merged worktrees only after their commits and evidence are recoverable
from the remote branch or merged PR.
