# Evidence-gated harness evolution

## Purpose

Harness evolution improves instructions, examples, memory curation, or routing
from measured project outcomes while keeping models, tools, permissions,
credentials, gates, production, approval, and merge outside autonomous control.

This is not unrestricted self-modification. The repository implements an
offline comparison kernel:

```text
PROJECT OUTCOME
      ↓
SANITIZED AGGREGATE SIGNAL
      ↓
BOUNDED CANDIDATE PROPOSAL
      ↓
INCUMBENT AND CANDIDATE RUN THE SAME PROTECTED CASES
      ↓
QUALITY + REGRESSION + SAFETY + COST + LATENCY GATES
      ↓
PASS → HUMAN-REVIEWED PR
FAIL → REJECT OR REVISE
```

A passing comparison authorizes only human review. It never promotes a
candidate.

## Two improvement loops

The existing ecosystem loop observes external changes and decides whether the
repository should investigate them. Harness evolution uses internal outcome
evidence to test a bounded behavioral change.

| Loop | Input | Output | Adoption authority |
|---|---|---|---|
| Ecosystem research | Specifications, releases, repositories, research | Ledger finding or proposal | Human review and merge |
| Harness evolution | Sanitized project outcomes and protected cases | Candidate comparison report | Human review and merge |

Model-weight training is a separate parametric loop and is not implemented by
this repository.

## Committed components

| Artifact | Responsibility |
|---|---|
| `.agentic/evolution/policy.json` | Closed authority, threshold, path, and privacy contract |
| `.agentic/evolution/incumbent.json` | Last-known-good synthetic starter evaluation |
| `.agentic/evolution/eval-sets/harness-regression.jsonl` | Human-owned protected cases |
| `.agentic/evolution/schemas/` | Closed signal and evaluation-result formats |
| `scripts/evolution_engine.py` | Offline deterministic validator and comparator |
| `harness-evolution` skill | Operating and routing contract |

The starter incumbent is a deterministic contract fixture, not a claim about
production performance. Downstream projects must replace synthetic cases with
domain-owned, human-reviewed evals before drawing product conclusions.

## Allowed curriculum

Start with the lowest-risk surface that can address the observed failure:

1. Few-shot examples.
2. Instructions.
3. Memory curation.
4. Routing.

Tool definitions, hooks, dependencies, permissions, credentials, MCPs,
security policy, workflows, deployment, production, and model weights do not
enter the committed loop. Those require separate architecture and security
decisions.

## Signal boundary

Only bounded aggregates enter the loop. Raw prompts, outputs, source code,
secrets, credentials, personal data, email addresses, and user identifiers are
forbidden fields. A signal declares:

- source type and opaque provenance reference;
- outcome class;
- normalized quality, safety, cost, and latency metrics;
- non-identifying labels;
- explicit redaction and aggregate-only retention flags.

The validator does not redact raw material. It rejects evidence that is not
already sanitized. Production collection, retention, tenant isolation,
deletion, consent, and access control require a separate data architecture.

## Exam integrity

Candidate and incumbent results must carry the exact SHA-256 fingerprints of
the committed policy and eval set. They must cover the same unique cases, and
the candidate must declare every changed path.

The candidate cannot own:

- the evolution policy or eval set;
- its comparison engine;
- security hooks or security model;
- CI workflows;
- dependencies;
- credentials or runtime configuration.

Protected changes require a separate governance PR. Never combine a candidate
change with a weaker exam or promotion threshold.

The comparator validates declared candidate paths. The pull-request reviewer
must reconcile that declaration with the actual diff and obtain every review
reported for the selected surfaces. Git history, code owners, and branch
protection—not candidate evidence—remain authoritative for changed files.

## Promotion contract

`PASS` requires:

- a positive weighted quality gain;
- zero protected regressions;
- zero safety failures;
- cost and p95 latency within policy budgets;
- complete evidence coverage;
- an allowed change surface;
- evaluator independence.

Even then, `promotion.authorized` remains `false`. Normal issue, task, branch,
PR, code-owner, security, and human merge rules remain authoritative.

## Enterprise extension boundary

An enterprise product may later add opt-in signal adapters, calibrated judges,
hidden holdouts, statistical confidence, encrypted trace storage, tenant
isolation, canaries, and rollback automation. None is implied by this offline
kernel. A deployment or canary requires a separate production change contract.
