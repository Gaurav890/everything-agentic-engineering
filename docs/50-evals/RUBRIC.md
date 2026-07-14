# Evaluation rubric

A task is not done because an agent says it is done.

## Gate 1 — Traceability

- Requirement IDs identified.
- Acceptance criteria identified.
- Scope did not silently broaden.

## Gate 2 — Functional evidence

- Happy path verified.
- Failure paths verified where relevant.
- Edge cases from PRD tested.

## Gate 3 — Engineering evidence

- Formatting/lint passes.
- Typecheck passes where applicable.
- Relevant tests pass.
- No known broken baseline is hidden.

## Gate 4 — UI evidence

For UI work:
- Running app inspected.
- Important responsive breakpoints checked.
- Keyboard access checked.
- Loading/empty/error/success states checked.
- Reduced-motion behavior considered.
- Separate critic/evaluator reviewed substantial UI.

## Gate 5 — Security evidence

For sensitive work:
- Threat model updated.
- Auth/authz verified.
- Secrets not leaked.
- Input boundaries reviewed.
- Relevant abuse cases tested.

## Gate 6 — Durable state

- Docs reflect reality.
- CURRENT_STATE updated if truth changed.
- PROGRESS appended with evidence.
- HANDOFF updated.
- ADR/design decision recorded when needed.

## Verdicts

- PASS
- PASS_WITH_RISKS
- FAIL
- BLOCKED
