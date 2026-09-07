# Product requirements document

Status: Active

## 1. Problem

Generic starters either produce polished-looking demos without engineering
credibility or enterprise scaffolds with no product taste. New users face too
many commands, irrelevant profiles, blank documents, and unclear production
boundaries.

## 2. Desired outcome

A person can answer a small set of consequential questions, see materially
different live answers to the same product problem, and receive a visually
distinctive project with one complete, testable journey, durable requirements,
explicit authority boundaries, and exactly one next action.

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

Start one creative-direction sprint, compare product-specific live directions
(without a fixed catalog limit), approve or synthesize one, compile tokens, and
verify the running result.

### UJ-004 — Research-to-build journey

Choose whether current evidence should shape the first pass, use Perplexity or
a disclosed primary-source/manual fallback when selected, synthesize findings
into the product brief, and see the full path from research through human review
without learning internal commands.

## 6. Non-goals

See `NON_GOALS.md`. Generation does not authenticate, install dependencies,
connect production services, deploy, approve, or merge.

## 7. Functional requirements

### FR-001 — Minimal credible project creation

The guided generator must select only relevant profiles, preserve durable
product context, create a runnable onboarding workspace or explicitly chosen
reference experience, and expose one safe next action. A finished custom
product requires the subsequent guided design and implementation session.

### FR-002 — Enterprise workflow contract

Enterprise generation must capture business object, tenancy, approval model,
and data sensitivity; create role, workflow, evidence, audit, and adapter
contracts; and supply a working local request-decision vertical slice.

### FR-003 — Product-specific visual system

Web products must make a creative-direction sprint the default first design
action and support materially different, responsive project-owned directions
without a fixed shortlist. Candidates must diverge on named experiential axes,
use realistic product content and states, and document their signature idea,
asset strategy, purposeful motion, responsive behavior, and reduced-motion
behavior. The three bundled examples are an explicit reference option and may
not qualify as a custom project's answer. Require live evidence and human
approval before canonical token compilation.

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

### FR-006 — Personalized, resumable onboarding

Creation captures project intent, open preferences, and a native client choice;
generates product-owned draft documents; and provides a consent-based handoff
without credentials or installation. Custom/existing-brand projects use an
open-ended local candidate catalog. Approval is tied to the candidate, brief,
intake, listed preview sources, and evidence. The user can reject all options,
change direction, or resume without repeating settled questions.

### FR-007 — Visible research-to-build journey

Guided creation must explicitly offer Perplexity-first current research and a
no-research fast path. Selection persists in the project brief and profile
manifest, with the active profile controlling routing and the brief retaining
provenance. When selected, the generated project creates a bounded source-ledger
contract plus validated machine state bound to the source ledger and a
changed/no-change brief decision, and routes research before product/design
decisions while supporting a disclosed primary-source/manual fallback. Copied
or unbound research text must not advance the workflow. One read-only journey command must
show research, product, design, build, verification, review, their current
states, and the exact next action. Creation never collects credentials, installs
or starts an MCP server, or performs network research.

### FR-008 — One-command guided Project Studio

`./agentic start` must be the public entry point for both creating a new project
and resuming a generated one. The first interaction asks for the product,
audience, and desired outcome in plain language, then presents an editable route
recommendation. Internal profiles, task IDs, skills, providers, and evidence
machinery stay behind progressive disclosure. The generated Studio must show a
profile-relevant product → direction → build → proof journey, preserve settled
answers, disclose unresolved decisions and capability limits, and expose one
clear continuation without conflating research, design, token, implementation,
evaluation, or human approval authority.

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
- a fresh custom project reaches live product-specific candidates through one
  obvious command, and theme-only or starter-demo candidates fail closed;
- the first README screen communicates one outcome, one start command, visible
  proof, and the research-to-review journey without requiring platform knowledge;
- local-versus-production boundaries are visible in UI and documentation;
- full repository verification and release smoke pass;
- broad self-service claims remain blocked until five consented anonymous
  newcomer sessions satisfy the published pilot gate;
- final evaluator is separate from the builder and a human approves merge.
- the same `./agentic start` entry point creates or resumes a project, and its
  default first interaction contains no internal profile, task, skill, MCP, or
  evidence terminology;

## 11. Acceptance criteria

See `ACCEPTANCE_CRITERIA.md`.
