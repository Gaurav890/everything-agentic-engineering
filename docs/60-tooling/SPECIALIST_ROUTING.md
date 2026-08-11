# Specialist capability routing

The broker turns reviewed expertise into task-level action without installing
an agent collection or launching every available role.

```text
TASK EVIDENCE
→ PROFILE GATE
→ SMALLEST CAPABILITY MATCH
→ ONE ACCOUNTABLE OWNER
→ REQUIRED DELIVERABLE
→ INDEPENDENT EVALUATOR
→ PR EVIDENCE
```

## Use it

```bash
./agentic agents list
./agentic agents list --domain security
./agentic agents show identity-access
./agentic agents recommend T-009
./agentic agents doctor
```

`./agentic task plan T-009` includes the same deterministic recommendations.
JSON output is available on `list`, `show`, `recommend`, and `doctor` for other
tools and agent runtimes.

## How selection works

The broker reads:

- the task title, goal, owner, risk, owned files, and verification gates;
- optional explicit `specialist_ids` recorded in the task;
- selected and resolved project profiles;
- reviewed terms, paths, authority, and when-not-to-use rules in
  `.agentic/external-agents.json`;
- optional activated contracts in `.agentic/project.json`.

Required risk matches are returned first. Optional matches are capped so the
task does not accumulate a committee. No match is a legitimate outcome.

An explicit task specialist may cross a profile gate only because the reviewed
task itself records the exception. The project owner should explain that choice
in the PR.

## Activation is not installation

Activation is an optional preference for repeated matching work:

```bash
./agentic agents activate identity-access --dry-run
./agentic agents activate identity-access --yes
./agentic agents deactivate identity-access --yes
```

It changes only `.agentic/project.json`. It does not download or execute an
upstream prompt, add a plugin or MCP, select a model, expose credentials, widen
the sandbox, allow network access, deploy, approve, or merge.

## Ownership and evaluation

- One existing project role remains accountable for implementation.
- A specialist provides a bounded artifact or review within declared authority.
- Overlapping capabilities enrich the local role rather than create duplicate
  writers.
- Builder and final evaluator remain separate.
- A required specialist is complete only when its declared deliverable is
  present and evaluated.

Record the selected contract, rationale, authority, deliverable, evidence, and
evaluator in the pull-request template.

## Extending the catalog

Do not add an upstream personality prompt merely because it sounds useful. A
new contract needs:

1. pinned provenance and compatible license;
2. a real recurring task or risk gap;
3. precise terms, paths, and profile gates;
4. declared owner, authority, deliverable, evaluator, and non-use rule;
5. routing fixtures and safety tests;
6. human-reviewed pull request.

Prime Agent or another execution runtime is not implied by this catalog. A
runtime integration would need its own architecture, threat model, permission
model, tests, and approval.
