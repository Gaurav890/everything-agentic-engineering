---
name: loop-engineering
description: Execute a bounded autonomous engineering loop with explicit goal, context, allowed actions, acceptance criteria, retry budget, evidence, persistent state, and safe terminal states.
---

# Loop engineering

Use this contract for every meaningful autonomous task.

## Contract

```yaml
loop:
  id: LOOP-XXX
  task_id: T-XXX

  goal: one bounded outcome

  requirements:
    - FR-XXX

  acceptance:
    - AC-XXX

  inputs:
    - exact relevant files only

  allowed_actions:
    - read
    - edit scoped files
    - run local tests

  forbidden_without_human_approval:
    - production deployment
    - destructive database migration
    - credential change
    - billing or DNS change
    - irreversible external action

  verify:
    - exact commands or observations

  budget:
    max_attempts: 3

  terminal_states:
    - DONE
    - BLOCKED
    - NEEDS_HUMAN
    - FAILED_SAFE
```

## Runtime

1. **Goal** — state the exact outcome.
2. **Context** — read the smallest relevant durable state.
3. **Plan** — choose the next falsifiable step.
4. **Act** — make the smallest coherent change.
5. **Verify** — collect real evidence.
6. **Diagnose** — if failed, update hypothesis.
7. **Retry** — only within budget and only with a changed hypothesis/new evidence.
8. **Record** — update task and durable state.
9. **Decide** — next task or terminal state.

## Anti-patterns

Never:
- loop forever,
- retry identical commands without learning,
- let the same agent self-certify purely by confidence,
- hide failing tests,
- broaden scope silently,
- write "done" without evidence.

## Completion evidence

Record:
- command/test,
- result,
- affected acceptance criterion,
- evidence file or output summary,
- known limitations.
