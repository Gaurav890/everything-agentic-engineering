# Agent operating agreement

This file mirrors the repo's agent conventions for tools that understand `AGENTS.md`.

## Goal

Keep the main context focused on requirements, decisions, task state, and integration. Quarantine noisy exploration, logs, research, and audits inside specialized agents.

## Default team

| Agent | Owns | Default write access |
|---|---|---|
| orchestrator | task graph, delegation, merge order, final synthesis | execution docs only |
| product | PRD, requirements, acceptance criteria | product docs |
| architect | architecture, contracts, data model, ADRs | engineering docs |
| frontend | web UI implementation and visual evidence | web/UI-owned files |
| backend | APIs, auth, jobs, database | backend-owned files |
| mobile | Expo/React Native | mobile-owned files |
| researcher | live research and source ledger | research docs |
| security | threat modeling and security findings | security docs only unless assigned a fix |
| qa-evaluator | adversarial verification | eval evidence |
| integration-reviewer | cross-layer review | read-only by default |

## GitHub integration rules

1. Normal committed work happens on a short-lived task branch, not directly on `main`.
2. Branches use `<type>/<TASK-ID>-<slug>`.
3. Draft PRs are the preferred shared surface for in-progress implementation collaboration.
4. Every meaningful PR links task IDs, issues when applicable, requirements, acceptance criteria, and evidence.
5. Workers move implemented tasks to `review`. Before final merge, `prepare-merge.sh` may write `done` on the task branch; only the merged state on `main` is authoritative.
6. Squash merge is the default.
7. Agents follow the same review, security, CODEOWNERS, and protected-branch rules as human contributors.

See `docs/70-collaboration/GITHUB_WORKFLOW.md`.

## Parallelization rules

1. Build a dependency DAG before parallel write-heavy work.
2. Assign one owner per file or tightly coupled module.
3. Use separate worktrees for independent code branches.
4. Workers verify their own scope.
5. Evaluators independently test the claim.
6. Orchestrator opens or updates the PR and merges only after evidence, required review, and checks are present.
7. Update durable state as part of the branch/PR, then mark the task `done` only after merge.

## Agent result contract

Every specialist returns:

```md
## Outcome
DONE | BLOCKED | NEEDS_HUMAN | FAILED_SAFE

## Scope
Exactly what was attempted.

## Changes
Files changed or artifacts created.

## Evidence
Commands, tests, screenshots, URLs, or inspected behavior.

## Risks
Remaining risks and assumptions.

## Handoff
Exact next action.
```

## Context discipline

Do not paste entire logs into the main thread. Return the smallest useful summary and point to durable evidence files when needed.
