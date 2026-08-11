# Parallelization plan

## Dependency DAG

```text
T-030 Specialist capability broker
  └── T-031 Capability decision engine and shared adapter contract
        ├── T-032 Optional Prime Agent adapter
        └── T-033 Selective Agency Agents installation planner
```

T-032 and T-033 are implemented concurrently from T-031's coordination
checkpoint. They remain stacked behind T-031 until the shared contract lands.

## File ownership

| Task | Agent | Files/modules owned | Shared state touched | Parallel-safe? |
|---|---|---|---|---|
| T-031 | Orchestrator / capability-engine builder | Shared manifest schema, capability command, routing skill, public docs, integration tests | Task and execution ledgers; command registry | Yes, after the coordination checkpoint; only T-031 edits shared state |
| T-032 | Prime Agent adapter specialist | `prime-agent.json`, `prime_agent.py`, Prime Agent guide, adapter tests | None | Yes |
| T-033 | External-agent supply-chain specialist | `agency-agents.json`, `agency_agents.py`, selective-install guide, planner tests | None | Yes |

## Worktree plan

| Task | GitHub issue | Branch/worktree | PR | Merge target | Merge order |
|---|---|---|---|---|---|
| T-031 | #42 | `feat/T-031-capability-decision-engine` / `t-031-capability-decision-engine` | Draft, opened after full verification | `main` | 1 |
| T-032 | #43 | `feat/T-032-prime-agent-adapter` / `t-032-prime-agent-adapter` | Stacked draft | T-031 branch, then `main` after T-031 lands | 2 |
| T-033 | #44 | `feat/T-033-trusted-external-installer` / `t-033-trusted-external-installer` | Stacked draft | T-031 branch, then `main` after T-031 lands | 2; independent of T-032 |

## Verification gates

- Validate every capability manifest against the same schema.
- Prove default commands are read-only and produce stable JSON.
- Prove adapters reject bulk/global/automatic or authority-expanding behavior.
- Run each adapter's focused tests in its worktree.
- Rebase dependent branches onto the verified T-031 integration commit and run
  the full repository suite before any PR is marked ready.
- Builder and final reviewer remain separate; no agent self-approves or merges.

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

Open draft PRs early so the dependency chain is visible. T-031 lands first.
T-032 and T-033 are then updated from `main`, verified again, and reviewed as
separate security-sensitive changes. Each PR links exactly one issue and task.

## Integration order

1. Merge T-031 after human review and required checks.
2. Update T-032 and T-033 from the new `main` in their isolated worktrees.
3. Run targeted and full verification independently.
4. Merge T-032 and T-033 in either order after separate human approval.

Do not mark a task `done` until its PR is merged. No task may install or enable
Prime Agent, Agency Agents, credentials, providers, MCPs, network access,
sandbox authority, production access, approvals, or merge authority.
