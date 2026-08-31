# Handoff

Last updated: 2026-08-30

## Current goal

Measure whether five newcomers can create, personalize, implement, verify, and
continue one useful web feature without maintainer intervention.

## Implemented

- Project-owned brief, README, product/design/engineering drafts and first feature.
- Consent-based native handoff and manual app/editor instructions; no key collection.
- Open custom/existing-brand catalogs and explicit optional reference mode.
- Evidence-bound approval and stale-context/source/evidence detection.
- Responsive workspace with saved intent, continuation, candidate links, copy
  feedback, visible keyboard focus and context-error recovery.
- Consent-based local P1–P5 pilot packets, closed anonymous scorecards, strict
  privacy validation, aggregate thresholds, repeated-blocker detection, and
  read-only summary output unless a new report path is explicitly confirmed.

## Evidence and limits

See `docs/50-evals/evidence/T-047/` for implementation checks and limits. The
deterministic evaluator has synthetic regression coverage; that coverage is not
a participant result. Native sign-in and live assistant sessions have still not
been measured through the pilot.

No newcomer study, production readiness, native implementation, launch,
deployment, human task approval or merge is implied.

## Exact next action

Run `./agentic pilot plan`, recruit five consenting people who did not build the
repository, and give each only the public README. Keep session packets private.
Use the aggregate result to choose the next small onboarding fix; do not claim
measured self-service success from tests or an incomplete sample. Existing-
project migration remains a separate reviewed change.
