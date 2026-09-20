# Product-to-Proof Studio

Status: Under review as the implementation contract for T-055 through T-059

## Category

Everything Agentic Engineering is a local-first **Product-to-Proof Studio**:

> Turn an idea into a distinctive, production-credible product—with governed
> execution and evidence.

It is not primarily a prompt library, theme catalog, coding-client wrapper, or
PR factory. The product advantage is the continuous path from product judgment
and visual direction to implementation, recovery, and proof. Claude Code,
Codex, and manual/editor work are execution adapters behind that path.

“Production-credible” means the product has explicit production boundaries,
adversarial checks, recovery behavior, and evidence that a production owner can
evaluate. It does not mean production-ready, deployed, compliant, or safe for
real customer data by default.

## The four activities

| Activity | Question answered | Durable output | Human gate |
|---|---|---|---|
| **Shape** | What outcome matters, for whom, and how will we know? | research decision, audience, promise, journey, metrics, constraints | product scope |
| **Design** | What should this product feel like and how does that survive change? | live directions, references, interaction/motion rules, semantic tokens, platform rules | direction and canonical tokens |
| **Build** | What can safely happen now, in what order, and who owns it? | dependency graph, waves, worktrees, runtime packets, journal, recovery state | wave continuation and integration |
| **Prove** | What evidence justifies the next consequential decision? | tests, screenshots, audits, independent verdicts, release packet | evidence, release, deployment, merge |

The Studio may expose detailed stage data, but it presents exactly one primary
action. Unknown or contradictory state produces `NEEDS_HUMAN`, never a guessed
success or approval.

## Primary screen contract

The first screen must make these items visible without opening advanced tools:

1. the current product outcome and next action;
2. settled and unresolved decisions;
3. design candidates and approval freshness;
4. task dependencies, waves, and writable ownership;
5. active workers, runtime, checks, cost when available, and failures;
6. evidence completeness and the next human gate.

Advanced commands remain available. They are not the information architecture.

## Entry and fallback

`./agentic start` remains the only public doorway. In T-055 it will ask before
starting a loopback-only Studio. When frontend dependencies are unavailable it
must print one exact installation command and continue in a terminal view over
the same project state. The browser and terminal must not maintain competing
truth.

The Studio does not ask for provider passwords, subscription tokens, or API
keys. It detects existing supported CLI authentication read-only and explains
manual alternatives.

## Supervised execution contract

The advanced command family reserved for T-056 is:

```text
./agentic run plan
./agentic run start
./agentic run status
./agentic run pause
./agentic run resume
./agentic run cancel
```

All implementations must conform to the versioned files under
`.agentic/schemas/` and the policy in `.agentic/product-to-proof.json`.

- A plan is an immutable snapshot bound to the SHA-256 of `TASKS.jsonl`.
- The planner rejects missing dependencies, cycles, and overlapping writable
  ownership before a worker is prepared.
- Independent tasks form maximally filled, task-ID-sorted Kahn ready sets of at
  most three workers by default; the same plan always produces the same waves.
- Every writable task receives its own non-default branch and unique worktree
  beneath a reviewed canonical worktree parent. Git registration, branch, and
  base commit are rechecked before launch or mutation.
- Every wave pauses for integration evidence and an explicit human continue.
- Events use closed typed payloads, contiguous sequence numbers, and a SHA-256
  chain over canonical RFC 8785 JSON bytes. Sequence 1 is the only event with a
  null previous hash. Reordering, deletion, duplication, truncation, or replay
  fails reconciliation.
- Reconciliation checks Git, worktrees, processes, checks, and pull requests.
  A stale `running` record is evidence of uncertainty, not success.
- T-056 must implement the declared loop rule: the same normalized failure
  fingerprint on attempt two requires a diagnosis record, and a third
  unsuccessful attempt moves the run to `NEEDS_HUMAN`. T-054 does not claim
  that executor behavior is already available.

No worker may approve itself, write to `main`, deploy, or merge.

The authoritative validator runs Draft 2020-12 schema and format validation
before semantic validation. It checks invariants JSON Schema cannot express:
unique tasks, dependency existence and acyclicity, deterministic maximal waves,
provider consistency, ownership collisions, journal transitions and continuity,
fresh evidence/decision identity, deterministic state replay, and safe terminal
state. The plan binds an exact base commit,
runtime version, user-owned model selection, invocation, permission/environment
fingerprints, network allowlist, MCP server/tool/config fingerprint, and the
reviewed action registry. Checks and tools are closed action IDs resolved to
structured argv/cwd/environment records and executed without a shell; user text
never becomes an executable command.

Before every mutation, T-056 must re-resolve the canonical project root and
each existing path ancestor, reject absolute/backslash/NUL/traversal paths and
symlink escape, and use no-follow or directory-descriptor-safe opens where the
platform permits. That immediate recheck limits but cannot eliminate TOCTOU on
a hostile local machine.

## Provider-neutral adapter

Every adapter implements the same lifecycle:

```text
doctor → prepare → launch → stream → interrupt → resume → reconcile → collect
```

Before launch, the operator sees the selected runtime, capability tier,
worktree, writable paths, tool/permission boundary, network and MCP state,
checks, retry budget, and stop conditions.

`fast`, `standard`, and `deep` describe task capability, not a secretly chosen
model. Model and provider mappings are owned by the user.

Each lifecycle call uses the closed adapter-operation schema. Requests bind the
plan, provider/version, worktree, non-default branch, writable paths, reviewed
action IDs, permission policy, invocation, capabilities, and timeout. Stream,
interrupt, resume, reconcile, and collect target an exact session, process, or
hash-bound checkpoint; resume additionally requires a resume token or verified
checkpoint. Outcomes normalize typed event/evidence IDs, session and process
identity, plus unsupported, denied, interrupted, retryable, fatal, and unknown
errors. Unknown capabilities, targets, or errors fail closed.

### Claude Code boundary

The future adapter may use documented non-interactive structured streaming,
explicit tool permissions, session IDs, interrupt, and resume behavior. A
non-bare run requires a trust preflight because project hooks and MCP servers
can load without an interactive trust prompt. Bare mode is not silently used
because it changes authentication and project-context behavior.

Source: [Claude Code programmatic execution](https://code.claude.com/docs/en/headless).

### Codex boundary

The future adapter uses `codex exec`, structured output, and the explicit
`workspace-write` sandbox with the user's existing CLI authentication. It does
not invoke a sandbox bypass or deprecated implicit automation flag.

Source: [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive).

### Manual/editor boundary

Manual mode produces the identical bounded work packet, ownership rules,
checks, and evidence requirements. It records no provider session and never
pretends a worker launched.

## Delivery gates

| Task | May begin when | Ships |
|---|---|---|
| T-055 | T-054 merged | loopback control plane and unified Studio |
| T-056 | T-055 merged | fixture-first supervised wave engine and opt-in runtime adapters |
| T-057 | T-056 contracts stable | governed Signalroom web/enterprise vertical slice |
| T-058 | shared contracts and tokens stable | runnable native companion and device evidence |
| T-059 | all prior evidence accepted | newcomer pilot, benchmark, public proof, release |

Each task uses a separate short-lived branch and PR. Human approval and merge
remain outside the Studio.

## State reduction and compatibility

Run state is a discardable read model rebuilt from an immutable plan and a
verified journal. Legal transitions and reducer version are declared in the
state schema. Terminal states cannot transition. A new reducer must replay the
unchanged source records and write a new atomic checkpoint; it never rewrites
the plan or journal. Unknown plan, event, evidence, decision, adapter, state,
or reducer versions fail closed until a reviewed migration exists.

## Claim discipline

This contract does not claim that the control plane, execution engine, final
Signalroom product, native application, benchmark results, or public launch
already exist. The current implementation state remains authoritative in
`docs/40-execution/CURRENT_STATE.md`.
