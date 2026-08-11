# Handoff

Last updated: 2026-08-10

## Current goal

Make reviewed specialist expertise discoverable and operational without
creating agent bloat, duplicate ownership, or implicit runtime authority.

## Completed

- Fourteen reviewed Agency Agents capabilities have pinned provenance,
  profiles, triggers, authority, deliverables, evaluators, and non-use rules.
- `./agentic agents` lists, explains, recommends, activates, deactivates, and
  validates local specialist contracts with human-confirmed mutation only.
- `./agentic task plan` includes specialist rationale and review evidence.
- Required security, payments, privacy, incident, accessibility, agent-trust,
  and multi-agent matches cannot silently disappear from the plan.
- The full upstream roster remains linked; no upstream agent is installed,
  copied, or executed by the broker.

## Blockers

- None.

## Unresolved decisions

- Future Agency Agents revisions or new local contracts require a new source,
  license, routing, safety, and evidence review.
- Prime Agent execution-runtime adoption remains out of scope and would need a
  separate architecture and threat-model decision.
- Activation remains optional because local roles can execute every contract.

## Verification status

- Broker routing, profile gates, JSON output, reversible activation, command
  discovery, and task-plan integration tests pass.
- `specialist-router` passes the platform skill validator.
- Full repository verification passes all ten stages across 29 tracked tasks,
  29 shared local skills, profiles, tokens, security hooks, runtime/Codex
  policy, local links, Showcase lint, typecheck, and tests.

## Exact next action

Use `./agentic task plan T-###` on the next reviewed task and record any routed
specialist's authority, deliverable, evidence, and independent evaluator.

## Relevant files

- `.agentic/external-agents.json`
- `.agentic/project.json`
- `.claude/skills/specialist-router/SKILL.md`
- `docs/60-tooling/AGENT_CATALOG.md`
- `docs/60-tooling/SPECIALIST_ROUTING.md`
- `scripts/agent_broker.py`
- `tests/test_agent_broker.py`

Keep this concise enough to read in under two minutes.
