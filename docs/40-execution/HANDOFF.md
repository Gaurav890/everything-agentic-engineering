# Handoff

Last updated: 2026-09-06

## Current goal

Validate whether newcomers can understand the promise, create a project, and
reach one useful verified product slice without maintainer intervention.

## Implemented

- One outcome-first public promise and a visible research → product → design
  → build → verify → review journey.
- An optional Perplexity-first research decision during guided creation, with a
  safe skip path, persisted profile state, and a generated research ledger.
- A research-aware assistant handoff with official-source and manual fallbacks;
  no credential collection, MCP installation or activation, or generator-time
  network research.
- A read-only `./agentic journey` view in text and JSON that distinguishes the
  whole path from the single action returned by `./agentic next`.
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

See `docs/50-evals/evidence/T-050/` for current implementation checks and
limits, and `docs/50-evals/evidence/T-049/` for the creative sprint. The
deterministic evaluator has synthetic regression coverage; that coverage is not
a participant result. The fresh-project page was inspected at desktop and 390px,
but a live assistant-generated candidate set, independent product/design review,
native sign-in, and newcomer sessions have still not been measured through the
pilot.

No newcomer study, production readiness, native implementation, launch,
deployment, human task approval or merge is implied.

## Exact next action

Run `./agentic pilot plan`, recruit five consenting people who did not build the
repository, and give each only the public README. Their route should exercise
the public promise, Perplexity choice or skip path, generated research contract,
handoff, and `journey` output. Use the aggregate result to choose the next small
fix; do not claim measured self-service or design-quality success from tests
alone.
