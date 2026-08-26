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
- A runnable request → evidence → review → decision → audit vertical slice.
- Pure workflow policy plus API, repository, and shared-type boundaries.
- Fail-closed tenant visibility, role, self-approval, evidence, rationale, and
  state-transition behavior.
- Loading, empty, invalid, failure, recovery, disabled, and success states.
- Three distinct direction systems with desktop/mobile Playwright evidence.
- Explicit local auth/persistence, disabled notification, and
  `production_ready: false` disclosure.
- A clean generated enterprise project that installs, verifies, builds, and
  passes its selected-archetype browser suite.

## Pending gates

- Independent product-quality and security/authority review.
- Human inspection and approval of the Linux visual candidates from successful
  Web quality run `33014674724` on PR #67.
- Full repository verification and release smoke at the committed branch head.
- Human approval of T-044 before PR finalization; no self-approval or merge.

## Exact next action

Review the six enterprise images in the `web-visual-baselines-linux` artifact
from run `33014674724`. If they are accepted, explicitly approve the T-044
Linux visuals so only those six files can be committed as canonical baselines;
then request independent reviewers against the final pushed head.

## Relevant files

- `.agentic/enterprise.json`
- `apps/web/app/enterprise-lab.tsx`
- `packages/domain/src/index.js`
- `packages/api/src/index.js`
- `scripts/project_generator.py`
- `docs/60-tooling/ENTERPRISE_GOLDEN_PATH.md`
- `docs/50-evals/evidence/T-044/`

Keep this concise enough to read in under two minutes.
