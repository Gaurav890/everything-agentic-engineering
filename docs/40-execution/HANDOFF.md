# Handoff

Last updated: 2026-09-10

## Current goal

Complete T-052 by raising the tested, read-only runtime floors to Claude Code
2.1.259 and Codex 0.153.0 using first-party release evidence while preserving
every optional capability and human approval boundary.

## Implemented

T-052 updates the machine-readable floors and cumulative trust-boundary records
for filesystem containment, credentials, concurrent managed-policy state,
project trust, durable review history, and selected-account MCP approvals. The
2.1.259 Bash argument-level deny expansion is explicitly excluded because
2.1.260 reverted it. Managed MCP servers, remote plugin
marketplaces, and experimental context management remain disabled and
human-gated. `/skill-doctor` is advisory and cannot automatically prune,
install, or mutate project skills. Focused tests, strict boundary simulations,
full verification, and independent security review now pass.

The most recent completed onboarding foundation includes:

- One outcome-first public promise and a visible research → product → design
  → build → verify → review journey.
- An optional Perplexity-first research decision during guided creation, with a
  safe skip path, profile-authoritative routing, a generated research ledger,
  and validated structured completion state.
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
- One profile-aware continuation: research-enabled projects enter `start`, while
  fresh design-critical web projects that skip research enter `design sprint`.
  Custom sprints require three live, product-specific, materially divergent
  candidates by default and reject starter-demo or duplicate-axis submissions.
- Candidate comparison exposes product states, signature idea, asset and motion
  rationale, responsive behavior, and reduced-motion behavior before approval.
- Evidence-bound approval and stale-context/source/evidence detection.
- Responsive workspace with saved intent, continuation, candidate links, copy
  feedback, visible keyboard focus and context-error recovery.
- Consent-based local P1–P5 pilot packets, closed anonymous scorecards, strict
  privacy validation, aggregate thresholds, repeated-blocker detection, and
  read-only summary output unless a new report path is explicitly confirmed.
- One public `start` doorway in the starter and generated projects, an
  outcome-first interview, editable plain-language route recommendation,
  provider/client progressive disclosure, persisted product idea, and a
  Shape → Direction → Build → Proof web Studio.

## Evidence and limits

T-052 has eight focused runtime-policy tests, strict lower-bound and exact-floor
simulations, stable read-only JSON evidence, full ten-stage verification, green
GitHub checks, and an independent security-review PASS at implementation commit
`202190e9512f0d27fa1ef77eea5f1db4d79aa50e`. Results are recorded under
`docs/50-evals/evidence/T-052/`.

The doctor verifies repository policy and minimum-version comparison; it does
not inspect actual user/managed runtime configuration or certify every later
release. No installation, upgrade, optional capability activation, production
readiness, deployment, approval, or merge is implied.

## Exact next action

Inspect draft pull request #84 and its evidence bundle. After a direct owner
decision, use the repository task workflow for the next lifecycle transition.
Issue #83 remains separately scoped.
