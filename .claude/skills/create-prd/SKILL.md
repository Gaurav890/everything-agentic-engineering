---
name: create-prd
description: Turn a product idea into a rigorous PRD with stable requirement IDs, user journeys, non-goals, edge cases, security/privacy considerations, metrics, and testable acceptance criteria.
---

# Create PRD

Use this skill when a product idea is vague, requirements are incomplete, or implementation should not begin yet.

## Process

### 1. Intake

Capture:
- problem,
- target user,
- current workaround,
- desired outcome,
- urgency,
- constraints,
- known dependencies.

### 2. Separate epistemic states

Maintain explicit sections:
- Facts
- Assumptions
- Open questions
- Decisions
- Non-goals

Do not convert an assumption into a fact silently.

### 3. Define journeys

For each major persona:
- trigger,
- starting state,
- happy path,
- alternate paths,
- recovery paths,
- terminal state.

### 4. Define requirements

Use stable IDs:

- `FR-001` functional requirement
- `NFR-001` non-functional requirement
- `AC-001` acceptance criterion

Every acceptance criterion must be observable and testable.

Bad:
> The page should feel fast.

Better:
> AC-014: On a warm cache under the agreed test environment, the primary route becomes interactive within the defined performance budget and no loading spinner remains after data resolves.

### 5. Cover non-happy states

Explicitly design:
- loading,
- empty,
- sparse,
- dense,
- invalid input,
- auth failure,
- authorization failure,
- offline/network failure,
- partial failure,
- retry,
- timeout,
- duplicate submission,
- dependency outage.

### 6. Security/privacy

Ask:
- What sensitive data exists?
- Who may read/write it?
- Where are trust boundaries?
- What abuse cases matter?
- What must never be logged?

### 7. Success

Define:
- product outcome,
- user outcome,
- operational metric,
- quality metric,
- launch gate.

### 8. Output

Update:
- `docs/10-product/PRD.md`
- `docs/10-product/ACCEPTANCE_CRITERIA.md`
- `docs/10-product/NON_GOALS.md`
- `docs/10-product/OPEN_QUESTIONS.md`

Do not begin implementation until blocking ambiguity is resolved or explicitly accepted.
