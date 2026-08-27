# Handoff

Last updated: 2026-08-26

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

## Pending gates

- Exact-head full verification, generated-project checks, release smoke, and
  normal Linux comparison after the independent-review corrections.
- Independent product-quality and security/authority re-review of the corrected
  committed head, as required by T-044.
- Pull-request finalization; no self-approval or merge.

## Exact next action

Finish the full local and clean-checkout gates, commit and push the review
corrections, then obtain independent product/QA and security PASS verdicts at
that exact head before task finalization.

## Relevant files

- `.agentic/enterprise.json`
- `apps/web/app/enterprise-lab.tsx`
- `packages/domain/src/index.js`
- `packages/api/src/index.js`
- `scripts/project_generator.py`
- `docs/60-tooling/ENTERPRISE_GOLDEN_PATH.md`
- `docs/50-evals/evidence/T-044/`

Keep this concise enough to read in under two minutes.
