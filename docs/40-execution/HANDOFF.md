# Handoff

Last updated: 2026-08-27

## Current goal

Take T-044's enterprise workflow golden path through independent product,
security, visual, and human review without confusing its credible local slice
with production readiness.

## Implemented

- One-command progressive onboarding with four enterprise-only domain questions.
- `.agentic/enterprise.json` and generated PRD, acceptance, journey, role,
  architecture, data, API, security, audit, and task contracts.
- A runnable request → evidence checks → submit → review → decision → audit
  vertical slice, including change/resubmission and cancellation.
- Pure workflow policy plus API, repository, and shared-type boundaries.
- Fail-closed tenant, role, requester-ownership, reviewer-eligibility,
  self-approval, evidence, policy-gate, rationale, and state-transition behavior.
- Trusted service-authored creation/evidence audit attribution; browser input
  cannot forge actor or transition metadata.
- Service-owned mutation timestamps and cancellation of stale refresh work.
- Executable single-review, dual-control, and policy-gated behavior.
- Loading, empty, invalid, failure, recovery, disabled, and success states.
- Three distinct direction systems with desktop/mobile Playwright evidence.
- Explicit local auth/persistence, disabled notification, and
  `production_ready: false` disclosure.
- A clean generated enterprise project that installs, verifies, builds, and
  passes its selected-archetype browser suite.
- Six human-approved Linux enterprise baselines across three directions and two
  viewports.
- A streamlined public README centered on real output, one-action onboarding,
  credible enterprise boundaries, design quality, and the commands users need.

## Verified review checkpoint

- Independent product-quality/adversarial QA and security/authority: PASS at
  `b0a9843ca0f9b9bf6517c1fefb25b4d5d20eda27`.
- Full repository verification, source build, 25 browser cases with one skip,
  24 visual comparisons, and clean-checkout release smoke passed.
- Fresh policy-gated and single-review projects with custom copy and business
  objects each built and passed 19 browser cases with seven expected skips.
- Evidence: `docs/50-evals/evidence/T-044/independent-review.md`.

## Exact next action

Resolve live state through `./agentic task closeout T-044` before choosing the
next operation. The bounded finalizer prepares approved tasks; the maintainer
performs the separate squash merge only after current required checks pass.
Closeout provides read-only cleanup guidance; do not execute cleanup
automatically.

This remains a local reference workflow. Production identity, tenant storage,
evidence services, durable audit, and idempotency require separate implementation
and review.

## Relevant files

- `.agentic/enterprise.json`
- `apps/web/app/enterprise-lab.tsx`
- `packages/domain/src/index.js`
- `packages/api/src/index.js`
- `scripts/project_generator.py`
- `docs/60-tooling/ENTERPRISE_GOLDEN_PATH.md`
- `docs/50-evals/evidence/T-044/`

Keep this concise enough to read in under two minutes.
