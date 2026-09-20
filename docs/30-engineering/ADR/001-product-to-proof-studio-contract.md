# ADR-001: Product-to-Proof Studio and supervised-run contracts

Status: Proposed for human review

Date: 2026-09-20

## Context

The repository already connects research, product shaping, creative direction,
tokens, implementation, evidence, and review, but the user experience exposes
too much of the underlying engineering machinery. Adjacent orchestration tools
make PRD-to-PR execution legible through simple commands, waves, recovery, and
monitoring. Matching only that surface would discard this project's stronger
product, design, enterprise, mobile, and proof ambitions.

We need one product contract before building a local control plane or launching
parallel workers. Otherwise UI, runtime adapters, journal semantics, mobile
work, and evidence can each invent incompatible state and authority models.

## Decision

Adopt **Product-to-Proof Studio** as the category and organize the product into
Shape, Design, Build, and Prove. Keep the detailed research/product/design/
system/build/verify/review lifecycle as the underlying model.

Adopt eight versioned JSON Schemas:

- immutable run plan bound to the task-ledger hash;
- append-only run events;
- reconciled derived run state;
- evidence records with artifact/check provenance and builder/evaluator separation;
- authenticated, evidence-bound human decisions;
- a closed action registry with structured executable, argument, directory,
  environment, network, timeout, and authority records;
- typed provider-neutral adapter operations;
- blind benchmark result.

Adopt one provider-neutral adapter lifecycle:

```text
doctor → prepare → launch → stream → interrupt → resume → reconcile → collect
```

Supervised execution defaults to maximally filled, task-ID-sorted Kahn ready
sets of three collision-free writable tasks per wave, one unique non-default
branch/worktree per task beneath a reviewed parent, and a human pause after
every wave. The T-056 reducer must fingerprint failures so a second identical
failure requires diagnosis and a third unsuccessful attempt requires human
intervention. T-054 declares that policy but does not claim the executor
exists. Stale process state never implies success.

## Security decisions

The future Studio is loopback-only with strict origin/session protection,
validated roots, and allow-listed no-shell actions. Plans bind an exact commit and
runtime/network/MCP/permission/environment fingerprints. Existing path
ancestors are canonicalized and rechecked before mutation; escaping symlinks,
absolute/device/traversal/NUL paths, and ambiguous separators fail closed. The
schemas prohibit automatic deployment, approval, merge, direct `main` writes,
and sandbox bypass. Runtime configuration and loaded hooks/MCPs are inspected
before launch. User text is data and is never interpolated into a shell command.

Journal events use closed typed payloads and a contiguous SHA-256 chain over
RFC 8785 canonical JSON. Authoritative replay loads and validates the exact
immutable plan and action-registry objects, recomputes their digests, and
requires exact wave, task, provider, branch, worktree, lifecycle, check,
evidence, and human-decision coverage before completion. State is derived by a versioned deterministic reducer,
written as an atomic checkpoint, and disposable. Terminal state cannot advance;
unknown versions and migrations fail closed. A newer reducer replays immutable
source records rather than rewriting them. Interrupt/resume/reconcile operations
must target an exact prior session, process, or hash-bound checkpoint.

## Consequences

### Positive

- browser and terminal views can share one state model;
- fixture adapters can test recovery before real runtime execution is enabled;
- Claude Code, Codex, and manual work remain interchangeable at the orchestration boundary;
- web, enterprise, and native proof can share semantics without sharing UI;
- public benchmark claims become auditable and failure-inclusive.

### Costs

- execution cannot ship as one large convenience script;
- schema migrations and backward compatibility require explicit ownership;
- pausing every wave is slower than unattended execution;
- real provider tests remain opt-in and environment-dependent;
- a static flow prototype is not evidence that the control plane works.

## Rejected alternatives

### Make a coding runtime the primary product

Rejected because it would make product/design/evidence subordinate to one
provider and weaken portability.

### Reuse UI state as execution truth

Rejected because browser state cannot safely recover processes, worktrees,
checks, or pull requests after a crash.

### Fully autonomous waves and final merge

Rejected because integration, release, deployment, and merge are consequential
human decisions, especially for enterprise workflows.

### Share web components with native mobile

Rejected because shared components encourage compressed desktop interaction.
Only domain contracts, APIs/types, semantic tokens, and governance vocabulary
are shared.

## Follow-up

- T-055 implements the loopback control plane against these contracts.
- T-056 implements fixture-first supervised execution and runtime adapters.
- T-057 and T-058 implement platform proof.
- T-059 runs the pilot and benchmark before public claims.
