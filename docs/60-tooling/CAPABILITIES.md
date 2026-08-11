# Capability decisions

The capability engine answers a narrow question:

> Which reviewed capability does this project or task justify, and what is the
> safest next action?

It does not install, execute, authenticate, activate, or grant authority.

```bash
./agentic capabilities list
./agentic capabilities show core-harness
./agentic capabilities plan --task T-031
./agentic capabilities doctor
./agentic capabilities plan --task T-031 --json
```

## Decision states

| State | Meaning | Normal next action |
|---|---|---|
| `built_in` | A committed local capability is present. | Use it within current task authority. |
| `recommended` | Profile/task evidence matches and detection passed. | Review the contract; invoke a local adapter manually only if justified. |
| `optional` | No current evidence justifies it. | Keep it inactive. |
| `missing` | Evidence matches but detection did not find it. | Review the plan-only adapter and seek separate approval for setup. |
| `blocked` | The reviewed contract forbids use. | Stop and resolve the documented risk through human review. |

`recommended` does not mean enabled, trusted for every task, or authorized.
`possible` authority in a manifest describes what a separately approved
integration might do; its default authority remains `none`.

## Evidence and precedence

The engine expands active profiles from `.agentic/project.json`, reads the
requested durable task from `TASKS.jsonl`, and matches explicit profile, term,
owner, and file-pattern evidence. It does not infer requirements from chat or
browser content.

Precedence is fail-safe:

1. An explicit blocked contract remains `blocked`.
2. A broken built-in contract is `missing` and fails `doctor`.
3. Matching evidence plus present detection is `recommended`.
4. Matching evidence plus absent detection is `missing`.
5. Everything else remains `optional`.

## Manifest contract

Capability manifests live under `.agentic/capabilities/*.json`. The schema is
strict so silent authority expansion fails validation. Each manifest records:

- immutable source provenance: HTTPS repository, full reviewed commit, license,
  and review date;
- explicit recommendation evidence;
- `none` as the default authority, plus disclosed possible and forbidden acts;
- `automatic: false` and `mode: plan_only`;
- a committed local adapter for non-built-in capabilities;
- path or command-name detection that checks existence only;
- rollback guidance and risks.

The engine validates adapter paths but never executes them. Adapters remain
separate, explicit surfaces for a human-reviewed plan or doctor operation.

## Non-negotiable boundary

Capability routing never performs or authorizes external installation, code
execution, login, provider/model/credential changes, MCP or network enablement,
sandbox widening, background services, production mutation, approval, or merge.
Those are separate workflows with separate human review.
