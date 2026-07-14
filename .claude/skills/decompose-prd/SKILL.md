---
name: decompose-prd
description: Convert a PRD into atomic implementation tasks with dependencies, file ownership, requirement traceability, verification methods, and parallelization safety.
---

# Decompose PRD

## Input

Read:
- PRD
- acceptance criteria
- architecture
- design system
- current state

## Task quality bar

Every task needs:
- `id`
- `title`
- `goal`
- `requirement_ids`
- `acceptance_ids`
- `owner`
- `depends_on`
- `status`
- `files_owned`
- `verification`
- `risk`
- `notes`

## Atomicity

A task should be:
- understandable independently,
- verifiable independently,
- small enough for one bounded loop,
- free of hidden cross-team ownership.

## Parallelization

Mark a task parallel-safe only if:
- dependencies are satisfied,
- file ownership does not overlap,
- shared mutable state is not being changed concurrently,
- merge order is defined.

## Output

Write JSON Lines to:
`docs/40-execution/TASKS.jsonl`

Then update:
`docs/40-execution/PARALLELIZATION.md`
