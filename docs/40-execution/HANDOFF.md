# Handoff

Last updated: 2026-09-06

## Current goal

Independently review the creative-direction sprint, then measure whether five
newcomers can create, choose, implement, verify, and continue one useful web
feature without maintainer intervention.

## Implemented

- Project-owned brief, README, product/design/engineering drafts and first feature.
- One shell-safe post-generation continuation command with a plain-language
  preview of the saved brief → journey → design → implementation → verification
  sequence and explicit non-launch/non-key-collection boundaries.
- Consent-based native handoff and manual app/editor instructions; no key collection.
- Open custom/existing-brand catalogs and explicit optional reference mode.
- One `./agentic design sprint` continuation for fresh design-critical web
  projects, with three live, product-specific, materially divergent candidates
  by default and deterministic rejection of starter-demo or duplicate-axis
  submissions.
- Candidate comparison exposes product states, signature idea, asset and motion
  rationale, responsive behavior, and reduced-motion behavior before approval.
- Evidence-bound approval and stale-context/source/evidence detection.
- Responsive workspace with saved intent, continuation, candidate links, copy
  feedback, visible keyboard focus and context-error recovery.
- Consent-based local P1–P5 pilot packets, closed anonymous scorecards, strict
  privacy validation, aggregate thresholds, repeated-blocker detection, and
  read-only summary output unless a new report path is explicitly confirmed.

## Evidence and limits

See `docs/50-evals/evidence/T-049/` for implementation checks and limits. The
deterministic evaluator has synthetic regression coverage; that coverage is not
a participant result. The fresh-project page was inspected at desktop and 390px,
but a live assistant-generated candidate set, independent product/design review,
native sign-in, and newcomer sessions have still not been measured through the
pilot.

No newcomer study, production readiness, native implementation, launch,
deployment, human task approval or merge is implied.

## Exact next action

Review the creative-sprint command routing, candidate contract, generated
workspace, and evidence without relying on the builder's verdict. Once the
reviewed change is on the default branch, run `./agentic pilot plan`, recruit
five consenting people who did not build the repository, and give each only the
public README. Use the aggregate result to choose the next small fix; do not
claim measured self-service or design-quality success from tests alone.
