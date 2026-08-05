# Parallelization plan

## Dependency DAG

```text
T-001
  ├── T-002
  └── T-003
        └── T-004
```

## File ownership

| Task | Agent | Files/modules owned | Shared state touched | Parallel-safe? |
|---|---|---|---|---|

## Worktree plan

| Task | GitHub issue | Branch/worktree | PR | Merge target | Merge order |
|---|---|---|---|---|---|

## Verification gates

## Runtime ceilings

Repository task budgets and ownership rules remain authoritative even when the
agent runtime permits more concurrency or nesting.

- Claude Code 2.1.217 introduced a default cap of 20 concurrently running
  subagents.
- Claude Code 2.1.219 changed the default nested spawn depth to three.
- Use `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` for a non-nested topology only
  after a maintainer approves the version-qualified runtime policy.
- Never infer that a runtime maximum is the correct project budget. Start with
  the smallest team that matches the dependency DAG and file ownership plan.

## PR strategy

For each task, decide whether to open a draft PR early, which reviewers/code owners are required, and what must merge first.

## Integration order

After each merge, update dependent branches from `main` before final verification. Do not mark a task `done` until its PR is merged.
