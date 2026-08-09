# Agent operating agreement

This file mirrors the repo's agent conventions for tools that understand `AGENTS.md`.

## Goal

Keep the main context focused on requirements, decisions, task state, and integration. Quarantine noisy exploration, logs, research, and audits inside specialized agents.

## Runtime adapters

This file is the cross-runtime contract and is loaded natively by Codex.

- Claude-specific runtime assets live under `.claude/`.
- Codex project configuration and hooks live under `.codex/`.
- `.agents/skills` exposes the canonical `.claude/skills` catalog to Codex by
  symbolic link; do not maintain a copied second catalog.
- `.codex-plugin/plugin.json` packages the same catalog as a skills-only Codex
  plugin.
- Run `./scripts/codex-doctor.sh` after Codex adapter changes.

The committed Codex adapter must not choose models/providers, add credentials,
register external MCP execution, enable network access, widen sandboxes, or
bypass approvals. Those require explicit, separately reviewed authority.

## Default team

| Agent | Owns | Default write access |
|---|---|---|
| orchestrator | task graph, delegation, merge order, final synthesis | execution docs only |
| product | PRD, requirements, acceptance criteria | product docs |
| architect | architecture, contracts, data model, ADRs | engineering docs |
| frontend | phase-routed product experience, web UI implementation, and visual evidence | web/UI-owned files |
| backend | APIs, auth, jobs, database | backend-owned files |
| mobile | Expo/React Native | mobile-owned files |
| researcher | live research and source ledger | research docs |
| security | threat modeling and security findings | security docs only unless assigned a fix |
| qa-evaluator | adversarial verification | eval evidence |
| integration-reviewer | cross-layer review | read-only by default |

## In-session Codex subagents

Project-scoped Codex role files live under `.codex/agents/` and translate the
read-heavy specialist responsibilities into native Codex custom agents:

| Codex role | Use for |
|---|---|
| `product_planner` | requirements, user needs, scope, non-goals, acceptance gaps |
| `architect` | boundaries, contracts, data flow, ADR implications, merge order |
| `researcher` | primary-source research, provenance, freshness, uncertainty |
| `design_critic` | independent running-product UX, accessibility, and token critique |
| `security_reviewer` | trust boundaries, authorization, secrets, and security tests |
| `qa_evaluator` | adversarial acceptance testing, regressions, and evidence gaps |
| `integration_reviewer` | cross-layer compatibility and final readiness review |

These roles are read-only, do not pin a model or reasoning level, do not add an
MCP server or network authority, and do not self-approve. Use Codex's built-in
`explorer` for general code mapping and the normal foreground worker for a
single implementation task.

Parallel write-heavy work requires a separate branch and worktree per owner.
Do not spawn several writable in-session subagents into the same checkout.

## GitHub integration rules

1. Normal committed work happens on a short-lived task branch, not directly on `main`.
2. Branches use `<type>/<TASK-ID>-<slug>`.
3. Draft PRs are the preferred shared surface for in-progress implementation collaboration.
4. Every new unfinished task records required issue references or an explicit
   reviewed issue-free reason. Every meaningful PR reproduces that contract,
   links its task, requirements, acceptance criteria, and evidence.
5. Workers move implemented tasks to `review`. Before final merge, `prepare-merge.sh` may write `done` on the task branch; only the merged state on `main` is authoritative.
6. Squash merge is the default.
7. Agents follow the same review, security, CODEOWNERS, and protected-branch rules as human contributors.

See `docs/70-collaboration/GITHUB_WORKFLOW.md`.

The deterministic `task-sync.sh` contract validates relationships and reports
live drift read-only. It never grants an agent authority to update issues,
tasks, PRs, approvals, or merges.

After merge, `task-closeout.sh` resolves current default-branch and GitHub
truth, detects transient handoff claims, and reports local cleanup commands.
Agents must not execute those commands automatically or encode predicted PR
outcomes as durable facts.

## Parallelization rules

1. Build a dependency DAG before parallel write-heavy work.
2. Assign one owner per file or tightly coupled module.
3. Use separate worktrees for independent code branches.
4. Workers verify their own scope.
5. Evaluators independently test the claim.
6. Orchestrator opens or updates the PR and merges only after evidence, required review, and checks are present.
7. Update durable state as part of the branch/PR, then mark the task `done` only after merge.

For separate terminals or Codex worktrees, follow
`docs/70-collaboration/PARALLEL_TERMINALS.md`. Treat shared execution ledgers as
orchestrator-owned integration files even though the launcher excludes them
from file-collision checks.

## Product-design routing

For substantial UI/UX work, the frontend owner invokes
`product-design-router` and runs only the design phases whose durable outputs
are missing or stale. Design direction must precede tokenization and
implementation. When visual constraints are unclear, `design-intake` records an
adaptive brief and compares rendered directions. Human approval must precede
canonical design-system and token changes. External skills remain specialist
inputs; the project brief, design system, and tokens remain authoritative. A
separate evaluator owns final critique of the running experience.

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
