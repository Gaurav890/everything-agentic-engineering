# Product requirements document

Status: Active

## 1. Problem

Generic starters either produce polished-looking demos without engineering
credibility or enterprise scaffolds with no product taste. New users face too
many commands, irrelevant profiles, blank documents, and unclear production
boundaries.

## 2. Desired outcome

A person can answer a small set of consequential questions and receive a clean,
visually distinctive project with one complete, testable product journey,
durable requirements, explicit authority boundaries, and exactly one next
action.

## 3. Users/personas

- founders and product engineers starting a new product;
- enterprise teams translating a governed workflow into software;
- designers and frontend engineers who need non-generic visual foundations;
- reviewers responsible for security, data, architecture, and release quality.

## 4. Jobs to be done

- turn product intent into a runnable vertical slice without prompt archaeology;
- compare real design directions before committing to a system;
- know what is demo-ready, what is production-ready, and what remains blocked;
- continue through issues, tasks, branches, reviews, evidence, and durable state.

## 5. User journeys

### UJ-001 — Guided creation

Run one command, answer only relevant questions, review one plan, create a
separate project, and receive one next action.

### UJ-002 — Enterprise request decision

Create a tenant-scoped request, validate evidence, assign an eligible reviewer,
record an approve/reject/change/cancel decision, and append an attributable
audit event.

### UJ-003 — Design approval

Compare the same product content across three desktop/mobile directions,
approve or synthesize one, compile tokens, and verify the running result.

## 6. Non-goals

See `NON_GOALS.md`. Generation does not authenticate, install dependencies,
connect production services, deploy, approve, or merge.

## 7. Functional requirements

### FR-001 — Minimal credible project creation

The guided generator must select only relevant profiles, preserve durable
product context, create a runnable archetype-specific experience, and expose
one safe next action.

### FR-002 — Enterprise workflow contract

Enterprise generation must capture business object, tenancy, approval model,
and data sensitivity; create role, workflow, evidence, audit, and adapter
contracts; and supply a working local request-decision vertical slice.

### FR-003 — Product-specific visual system

Web products must begin with three materially different, responsive direction
systems and require explicit human approval before canonical token compilation.

### FR-004 — Evidence-gated engineering workflow

Tasks must trace to requirements and acceptance criteria, use isolated branches
or worktrees when writing in parallel, pass relevant verification, receive
separate evaluation, and update durable state before merge.

### FR-005 — First-project continuation and honest verification

The read-only guide must use current profiles and task lifecycle state to move
from approved design into a bounded first feature, implementation, independent
review, and post-merge continuation. Verification must declare its scope;
missing tools, visual baselines, native implementations, or production
adapters must not be presented as completed evidence.

## 8. Non-functional requirements

### NFR-001 — Safety

No generated project may silently enable credentials, MCPs, specialists,
network access, production writes, deployment, approval, or merge authority.

### NFR-002 — Product quality

Important experiences cover loading, empty, sparse, dense, invalid, error,
disabled, recovery, and success states with responsive, accessible,
reduced-motion evidence.

### NFR-003 — Enterprise credibility

Tenant, role, workflow, audit, adapter, production-readiness, migration, and
rollback boundaries are explicit and fail closed.

## 9. Data, security, and observability

The reference enterprise slice uses deterministic local fixtures only. It must
not contain secrets or claim that browser actor switching is authentication.
Production adapters require separate data ownership, retention, audit,
idempotency, concurrency, observability, and threat-model review.

## 10. Launch criteria

- generated web, mobile, core, and enterprise projects validate independently;
- enterprise interaction, domain-policy, build, and Playwright suites pass;
- desktop/mobile evidence is human-reviewed across all three directions;
- local-versus-production boundaries are visible in UI and documentation;
- full repository verification and release smoke pass;
- final evaluator is separate from the builder and a human approves merge.

## 11. Acceptance criteria

See `ACCEPTANCE_CRITERIA.md`.
