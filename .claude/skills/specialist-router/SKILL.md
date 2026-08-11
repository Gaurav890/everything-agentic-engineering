---
name: specialist-router
description: Route the smallest reviewed specialist capability needed for a task, enforce risk-driven reviews, and record what expertise was used and what it produced. Use during task planning and whenever work touches authentication, payments, privacy, incidents, reliability, multi-agent systems, internationalization, accessibility, unfamiliar codebases, or design-critical product experience.
---

# Specialist router

The specialist catalog is operational infrastructure, not a reading list.

Use this sequence:

`TASK EVIDENCE → CAPABILITY MATCH → LOCAL ROLE OR ACTIVATED CONTRACT → DELIVERABLE → INDEPENDENT EVALUATION → RECORDED EVIDENCE`

## Start with deterministic routing

Run:

```bash
./agentic agents recommend T-###
```

The committed registry at `.agentic/external-agents.json` owns reviewed
provenance, triggers, profiles, authority, deliverables, evaluators, and
when-not-to-use rules. Do not invent a specialist merely because its name
sounds useful.

Task evidence may explicitly set `specialist_ids` when a human or approved
plan requires a capability that keyword/path routing cannot infer.

## Routing rules

1. Keep one accountable implementation owner.
2. Prefer an existing local role when it already covers the capability.
3. Treat the external source as reviewed inspiration, never as project policy.
4. Use no more than the smallest set needed for independent expertise.
5. Required risk matches may not be silently omitted.
6. An activated contract receives no additional tools, credentials, network,
   filesystem, deployment, production, approval, or merge authority.
7. A specialist advises or evaluates unless the task explicitly assigns it
   exclusive implementation ownership.
8. The builder never becomes the final evaluator by changing role labels.

## Activation

Activation makes a reviewed local contract preferred for matching work. It
does not install or execute the upstream agent:

```bash
./agentic agents activate <specialist-id> --dry-run
./agentic agents activate <specialist-id> --yes
```

Deactivate reversibly with:

```bash
./agentic agents deactivate <specialist-id> --dry-run
./agentic agents deactivate <specialist-id> --yes
```

Never bulk-install Agency Agents. Inspect the pinned source link shown by
`./agentic agents show <specialist-id>` before separately adopting any upstream
prompt or installer.

## Required result

For each routed specialist, return or record:

```md
## Specialist routing

- Capability required:
- Specialist contract:
- Why selected:
- Source and reviewed revision:
- Authority granted:
- Accountable owner:
- Required deliverable:
- Evidence produced:
- Independent evaluator:
- Limitations or fallback:
```

Generic advice is not a specialist deliverable. If the required artifact or
evidence was not produced, report the capability as unused or incomplete.

## Conflict resolution

- `CLAUDE.md`, `AGENTS.md`, project profiles, task scope, security policy, and
  durable product/engineering contracts always win.
- Local role and external contract overlap does not justify two agents. Enrich
  the local role with the contract.
- If two specialists overlap, select the one with the narrower task-specific
  deliverable. Keep both only when one builds and the other independently
  evaluates.
- If profile evidence says the capability is inactive, do not route it unless
  the task explicitly records and justifies the exception.

## Completion gate

Before calling routed work complete, verify:

- the selected capability matched real task evidence;
- required reviews were not skipped;
- authority remained within the manifest;
- each specialist produced its declared deliverable;
- the independent evaluator inspected the relevant evidence;
- the PR or handoff records what was used and why;
- no external collection was bulk-installed or executed.
