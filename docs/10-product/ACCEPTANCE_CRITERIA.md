# Acceptance criteria

Acceptance criteria are observable and testable.

## AC-001 — Guided project is relevant and actionable

**Linked requirements:** FR-001, FR-003

**Given** a user starts guided creation, **when** they choose a product surface
and confirm the plan, **then** the new directory contains only resolved
profiles, records product/design intent, enables no external authority, and
prints exactly one next action.

**Evidence required:** generator tests, generated-project verification, release
smoke, and desktop/mobile direction evidence.

## AC-002 — Enterprise workflow is credible but bounded

**Linked requirements:** FR-002, NFR-001, NFR-003

**Given** an enterprise workflow project, **when** requester, reviewer, auditor,
admin, self-approver, and cross-tenant actors exercise the request lifecycle,
**then** allowed transitions succeed, prohibited transitions fail closed,
evidence and rationale rules are enforced, audit events are appended, and the
UI identifies local adapters and `production_ready: false`.

**Evidence required:** pure domain tests, UI contract tests, Playwright allowed
and denied paths, and machine-readable enterprise manifest validation.

## AC-003 — Enterprise artifacts trace intent to implementation

**Linked requirements:** FR-002, FR-004

**Given** confirmed enterprise intake, **when** generation completes, **then**
the PRD, acceptance criteria, journeys, role matrix, data model, API contract,
security model, audit events, and initial task graph agree with the same
business object, tenant model, approval policy, and sensitivity.

**Evidence required:** generator assertions and generated-project full verify.

## AC-004 — Product quality is evidence-gated

**Linked requirements:** FR-003, FR-004, NFR-002

**Given** a substantial UI change, **when** it is proposed for merge, **then**
the running product has responsive, accessible, reduced-motion, state,
interaction, and visual evidence; builder and evaluator are separate; and
intentional baseline changes require human review.

**Evidence required:** web quality checks, reviewed screenshots, evaluator
report, and PR policy.

## AC-005 — A newcomer can continue without inventing the workflow

**Linked requirements:** FR-001, FR-004, FR-005

**Given** a generated project, **when** current profiles, prerequisites, design
state, or tasks change, **then** `next` reports one appropriate action without
mutation, inferring approval, or looping forever at verification. Task
dependencies and concurrent workstreams remain explicit. Unknown state fails
closed. Web checks require their local tools, propagate failures, and never
generate or approve visual baselines. Documentation separates local web,
native scaffold, automated checks, human review, and production readiness.

**Evidence required:** routing and verification regressions, fresh generated
projects, browser checks, independent review, and a runnable consent-based
newcomer pilot with closed anonymous scorecards and a fail-closed aggregate
gate. Real participant results remain a launch gate, not an implementation test
that can be simulated by the maintainer.

## AC-006 — A new project does not inherit a product or a forced aesthetic

**Linked requirements:** FR-006, FR-003, NFR-001

**Given** captured product intent, **when** creation completes, **then** its
README, vision, PRD, and acceptance drafts describe that product, its next step
is a prepared client handoff, and custom/existing-brand catalogs begin empty.
Blank optional preferences remain unresolved. No keys are collected, client
installed, or session launched without confirmation. Manual handoff works
without a supported terminal client.

**Given** a custom candidate, **when** it is registered and reviewed, **then**
arbitrary candidate counts and IDs work, a local preview and source list are
required, and incomplete intake or changed evidence cannot retain valid approval.

**Evidence required:** all-profile generation matrix, consent/argv tests,
symlink regression, candidate/freshness tests, actual generated-project browser
checks and screenshots, and independent review. A maintainer test is not a
newcomer usability study or proof of every downstream design's quality.
