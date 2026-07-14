# Team collaboration operating model

This repository supports humans and agents working together without turning chat messages into the only source of project truth.

## Ownership model

Every active work item has one accountable owner.

The owner is responsible for:

- Scope clarity.
- Keeping issue/task state current.
- Coordinating dependencies.
- Requesting the right reviewers.
- Ensuring verification exists.
- Driving the PR to merge or explicitly handing it off.

More than one person can contribute, but accountability should not be ambiguous.

## Shared work surfaces

Use each surface for its intended purpose:

| Surface | Use for |
|---|---|
| GitHub issue | Discussion, priority, ownership, external collaboration |
| `TASKS.jsonl` | Executable units, dependencies, agent routing, verification |
| Draft PR | Live implementation discussion and early feedback |
| PR review | Merge decision and code-specific feedback |
| `ADR/` | Durable technical decisions |
| `DESIGN_DECISIONS.md` | Durable design decisions |
| `CURRENT_STATE.md` | Present factual truth |
| `HANDOFF.md` | Exact continuity for the next person or agent |

Do not leave a critical decision only in Slack, email, a meeting transcript, or chat.

## Parallel work

Before parallel implementation:

1. Build the dependency DAG.
2. Assign one owner per file or tightly coupled module.
3. Create separate branches/worktrees.
4. Define integration order.
5. Define the contract between workstreams.
6. Merge the foundational contract change before dependent work when possible.

Example:

```text
T-101 API contract
  ├── T-102 backend implementation
  ├── T-103 web UI
  └── T-104 mobile UI
```

Preferred approach:

1. Merge the contract or fixture change first.
2. Let web/backend/mobile branches target that stable contract.
3. Avoid three branches inventing incompatible versions of the same interface.

## Handoffs

A good handoff states:

```text
Outcome
Current branch / PR
What changed
What is verified
What remains
Exact blocker
Files with active ownership
Known risks
Next concrete action
```

Do not write "almost done" without saying what remains and how completion will be verified.

## Conflict prevention

- Announce ownership before editing shared hotspots.
- Keep branches short-lived.
- Rebase or update from `main` before conflicts become large.
- Prefer stable interfaces between parallel workstreams.
- Resolve architecture disagreements in an ADR.
- Resolve requirement disagreements in product docs.
- Resolve merge order through the orchestrator for multi-agent work.

## Colleague review etiquette

- Review the change, not the person.
- Be specific about risk and desired outcome.
- Use severity labels in comments.
- Do not block on personal preference when project standards allow multiple valid choices.
- Authors should respond to every blocking comment with either a change or a reasoned resolution.

## Human + agent collaboration

Use agents for bounded work with clear evidence requirements.

A human or orchestrator should retain control over:

- Product ambiguity.
- Destructive actions.
- Production deployment.
- Credentials and billing.
- High-risk data migrations.
- Final merge decisions where policy requires human approval.

Agents may prepare branches and PRs, but they must follow the same branch, issue, review, security, and merge rules as colleagues.
