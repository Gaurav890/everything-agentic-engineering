# Handoff

Last updated: 2026-08-23

## Current goal

Finish verification and human review of the offline harness-evolution kernel.

## Completed

- Added a closed, versioned evolution policy with proposal-only authority.
- Added sanitized aggregate signal and evaluation-result schemas.
- Added five protected regression cases and a synthetic last-known-good
  incumbent with exact policy/eval fingerprints.
- Added deterministic quality, protected-regression, safety, cost, p95 latency,
  coverage, path, integrity, and evaluator-separation gates.
- Added `./agentic evolve` plus generated-project and repository tests.
- Documented the distinction between ecosystem research, harness evolution,
  model-weight training, and enterprise-only production extensions.

## Blockers

- No known implementation blocker.
- Independent security review is still required before the task can move to
  human approval.

## Unresolved decisions

- Whether to add an opt-in production signal adapter later. This requires a
  separate privacy, retention, access, tenant-isolation, deletion, and consent
  design.
- Whether domain teams should add calibrated judges, hidden holdouts,
  statistical confidence, canaries, and rollback automation. None belongs in
  this offline starter kernel by default.

## Verification status

- Thirteen focused evolution-engine tests pass.
- Agentic CLI and downstream project-generator tests pass.
- The committed policy, schemas, protected eval set, and incumbent validate
  offline with `mutation_performed: false`.
- Full repository verification passes all ten stages.
- Independent security review is pending.

## Exact next action

Open a draft pull request, obtain independent security review, and address any
findings before requesting direct human task approval. A passing candidate or
CI run never authorizes promotion or merge.

## Relevant files

- `.agentic/evolution/`
- `.claude/skills/harness-evolution/SKILL.md`
- `scripts/evolution_engine.py`
- `docs/30-engineering/HARNESS_EVOLUTION.md`
- `docs/50-evals/HARNESS_EVALS.md`
- `docs/60-tooling/EVOLUTION_POLICY.md`
- `tests/test_evolution_engine.py`
- `tests/test_project_generator.py`

Keep this concise enough to read in under two minutes.
