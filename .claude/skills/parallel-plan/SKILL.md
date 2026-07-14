---
name: parallel-plan
description: Create a safe multi-agent execution plan with a dependency DAG, file ownership matrix, worktree strategy, merge order, and verification gates.
---

# Parallel plan

## Step 1: Build DAG

For each work item identify:
- prerequisites,
- outputs,
- blocking dependencies,
- verification.

## Step 2: File ownership matrix

```md
| Task | Agent | Files/modules owned | Shared state touched | Parallel-safe? |
```

A task is not parallel-safe if another active task:
- edits the same file,
- changes the same schema without coordination,
- depends on its unmerged output,
- mutates the same external state.

## Step 3: Choose execution mode

Use:
- subagents for read-heavy isolated work,
- worktrees for independent write-heavy branches,
- agent teams only for genuine peer coordination.

## Step 4: Define merge order

Merge foundational contracts first:
1. schemas/types/contracts
2. backend/API
3. frontend/mobile consumers
4. integration fixes
5. evaluator/security gates

Adjust when the actual dependency graph differs.

## Step 5: Verification gates

Every worker verifies its own scope.
A separate evaluator verifies acceptance criteria.
The orchestrator verifies integration after merge.

## Output

Update:
`docs/40-execution/PARALLELIZATION.md`
and task entries in `TASKS.jsonl`.
