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

## PR strategy

For each task, decide whether to open a draft PR early, which reviewers/code owners are required, and what must merge first.

## Integration order

After each merge, update dependent branches from `main` before final verification. Do not mark a task `done` until its PR is merged.
