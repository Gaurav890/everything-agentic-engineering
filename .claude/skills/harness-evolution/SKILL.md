---
name: harness-evolution
description: Evaluate bounded harness candidates against the protected incumbent using sanitized outcome signals and deterministic quality, regression, safety, cost, and latency gates. Use when project evidence suggests instructions, examples, memory curation, or routing should improve; never use it to self-promote, change protected evals, expand authority, or train model weights.
---

# Harness evolution

Use the repository command surface:

```bash
./agentic evolve status
./agentic evolve signal validate <sanitized-signal.json>
./agentic evolve compare --candidate <candidate-results.json>
```

Follow:

`ACT → SANITIZE SIGNAL → EVALUATE → PROPOSE → COMPARE → HUMAN REVIEW → RECORD`

Read `docs/30-engineering/HARNESS_EVOLUTION.md` and
`docs/60-tooling/EVOLUTION_POLICY.md` before preparing a candidate.

Start with low-risk few-shot examples. Instructions, memory curation, and
routing require the reviews declared in `.agentic/evolution/policy.json`.
Protected policy, evaluation, security, workflow, dependency, credential,
permission, tool, and production surfaces are not candidate-owned.

The committed engine is offline and proposal-only. It may validate sanitized
signals and compare previously produced evaluation results. It must not ingest
raw production traces, invoke a remote model, implement its own proposal,
change its own exam, install or enable capabilities, deploy, canary, promote,
approve, or merge.

`PASS` means only that a candidate is eligible for independent human review.
It is never promotion authority.
