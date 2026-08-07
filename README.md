<div align="center">

# Everything Agentic Engineering

### Stop giving coding agents prompts. Give them an engineering system.

**A production-grade operating system for building and shipping software with AI coding agents.**

Turn an idea into:

**Discovery → UX Strategy → Product-Specific Design → Architecture → Parallel Agents → Evidence → Pull Request → Durable Memory**

<br />

[![GitHub stars](https://img.shields.io/github/stars/Gaurav890/everything-agentic-engineering?style=for-the-badge&logo=github)](https://github.com/Gaurav890/everything-agentic-engineering/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Gaurav890/everything-agentic-engineering?style=for-the-badge&logo=github)](https://github.com/Gaurav890/everything-agentic-engineering/network/members)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Release: v0.1.0](https://img.shields.io/badge/release-v0.1.0-111827?style=for-the-badge)](docs/releases/v0.1.0.md)

<br />

**Native Claude Code and Codex adapters. Designed for durable, evidence-gated agentic engineering.**

</div>

---

## From clone to an agent-ready task

![Everything Agentic Engineering quick-start flow](docs/assets/quickstart-flow.svg)

```bash
git clone https://github.com/Gaurav890/everything-agentic-engineering.git
cd everything-agentic-engineering
cp .env.example .env
./scripts/bootstrap.sh
./scripts/init-project.sh
```

In one guided path, the starter:

1. explains which capabilities your project actually needs;
2. keeps irrelevant web, mobile, backend, research, or design surfaces inactive;
3. records the selection in a machine-readable project manifest;
4. validates the environment without silently installing or deleting tools;
5. turns a durable task into a reviewed branch or worktree plan.

After product discovery and task decomposition create a ready task such as
`T-101`, inspect it without changing the workspace:

```bash
./scripts/task-plan.sh T-101
```

The planner is read-only. Workspace creation requires explicit confirmation,
and implementation, merging, deployment, and release remain separate human
decisions.

Read the [installation guide](docs/60-tooling/INSTALLATION.md), follow the
[60-second demo](docs/80-showcase/DEMO_SCRIPT.md), or review the
[v0.1.0 limitations](docs/60-tooling/COMPATIBILITY.md#known-limitations-in-v010).

---

## The problem

AI coding agents are incredibly capable.

But raw agent workflows still fail in predictable ways:

- Context disappears between sessions.
- PRDs drift away from implementation.
- Multiple agents modify the same files and create conflicts.
- The agent that builds the feature also decides whether its own work is good enough.
- Skills and MCP servers become an unmanageable collection with no clear routing.
- Parallel agents duplicate work instead of collaborating.
- Security exists as a prompt instead of an enforced gate.
- GitHub issues, branches, PRs, reviews, and human collaboration are afterthoughts.
- Long-running loops keep retrying without clear budgets or stop conditions.
- **"Done" means the agent said it was done.**

**Everything Agentic Engineering replaces that with one opinionated system.**

> The conversation is disposable. The repository is durable memory.

This is not another collection of hundreds of prompts, agents, skills, and MCP servers.

It is an engineering harness designed to answer a harder question:

> **How do humans and AI coding agents actually work together to take a product from idea to production without losing context, duplicating work, skipping verification, or destroying the Git workflow?**

---

## How it works

```mermaid
flowchart TD
    A[💡 Idea] --> B[🔎 Discovery + User Needs]
    B --> C[📋 PRD + Acceptance Criteria]
    C --> D[📊 Benchmark + UX Strategy]
    D --> E[🧭 Interaction + Agentic UX]
    E --> F[🎨 Design System + Tokens]
    F --> G[✅ Approved Product Experience]
    G --> H[🏗️ Architecture + Task DAG]
    H --> I[🎯 Orchestrator]

    I --> J[🎨 Frontend]
    I --> K[⚙️ Backend]
    I --> L[📱 Mobile]
    I --> M[🔬 Research]

    J --> N[🧪 Running-Product Audits]
    K --> N
    L --> N
    M --> N

    N --> O[🕵️ Independent Critic]
    O --> P[🔐 Security + Integration]
    P --> Q[🔀 Pull Request + Review]
    Q --> R[🚀 Merge]
    R --> S[🧠 Durable Memory]
    S --> T[🔁 Next Task]
```

The core operating loop is:

```text
GOAL
  ↓
READ DURABLE CONTEXT
  ↓
PLAN
  ↓
ACT
  ↓
VERIFY WITH REAL EVIDENCE
  ↓
┌───────────────────────────────────────┐
│ PASS          → RECORD → NEXT TASK    │
│ FAIL          → DIAGNOSE → RETRY      │
│ BLOCKED       → ESCALATE              │
│ RISKY         → HUMAN APPROVAL        │
│ BUDGET SPENT  → FAILED SAFE           │
└───────────────────────────────────────┘
```

No endless loops.

No agent marking its own work complete based only on confidence.

No relying on chat history as project memory.

---

## What is included

### ✦ A real reference product

`apps/showcase` contains **Signalroom**, an agent-operations console built
through the repository's complete product-design and evidence workflow.

It demonstrates planning, parallel workstreams, protected approvals,
pause/resume, recovery, durable artifacts, responsive layouts, required UI
states, accessibility checks, and an independent design critique.

#### Approve, pause, and resume a real run

The GIF below was captured from the running Signalroom app. It pauses and
resumes the selected run, then approves a protected read after showing scope,
masked fields, retention, and reversibility.

![Signalroom protected approval, pause, and resume flow](docs/assets/demo/03-signalroom-approval.gif)

#### Inspect required product states

Normal, loading, empty, and error are real selectable states in the showcase,
not screenshots invented for the README.

![Signalroom normal, loading, empty, and error states](docs/assets/demo/04-running-states.gif)

```bash
pnpm install
pnpm dev:showcase
```

See the [showcase brief](docs/80-showcase/BRIEF.md) and its
[evidence bundle](docs/50-evals/evidence/T-007/evidence.json).

### 🧠 Durable context that survives sessions

The repository, not the conversation, is the source of truth.

| Artifact | Responsibility |
|---|---|
| `CLAUDE.md` | Project constitution and universal agent rules |
| `NORTH_STAR.md` | Why the product exists |
| `PRD.md` | What must be built |
| `ACCEPTANCE_CRITERIA.md` | How success is objectively determined |
| `DESIGN_SYSTEM.md` | Visual and interaction contract |
| `packages/design-tokens/` | Machine-readable visual and interaction decisions |
| `ARCHITECTURE.md` | Technical boundaries and system structure |
| `ADR/` | Why important architectural decisions were made |
| `TASKS.jsonl` | Atomic executable work and dependencies |
| `CURRENT_STATE.md` | What is factually true right now |
| `PROGRESS.md` | Append-only verified progress |
| `HANDOFF.md` | Continuity for the next session or agent |
| `RUBRIC.md` | How implementation quality is judged |
| Git history | Durable checkpoints |

Important decisions leave the chat and enter version-controlled project artifacts.

---

### 🤖 Specialized agents

The starter includes focused agents for:

- **Orchestrator** — owns dependencies, delegation, parallelization, file ownership, merge order, and completion.
- **Product** — turns ideas into requirements, PRDs, journeys, non-goals, and acceptance criteria.
- **Architect** — defines technical boundaries, contracts, data models, and ADRs.
- **Frontend** — routes the required product-design phases, implements the approved experience, and captures running-product evidence.
- **Backend** — owns APIs, data, authentication, integrations, queues, and server-side logic.
- **Mobile** — handles React Native and Expo workflows.
- **Researcher** — performs current web research, crawling, documentation discovery, and source synthesis.
- **QA Evaluator** — tries to prove that the implementation is broken.
- **Security** — reviews trust boundaries, secrets, authorization, destructive actions, and vulnerabilities.
- **Integration Reviewer** — evaluates the complete system across product, frontend, backend, mobile, security, and documentation.

The system does **not** launch ten agents for every task.

> **Parallelize independent outputs, not shared state.**

---

### 🛠️ Project-local skills

Included skills:

```text
create-prd
decompose-prd
context-handoff
product-design-router
design-intake
discover
user-needs
benchmark
strategize
interaction-design
agentic-ux
design-system
design-tokens
responsive-audit
accessibility-audit
design-system-audit
token-audit
performance-ux
design-critic
polish
design-ops
research-ledger
parallel-plan
loop-engineering
security-gate
```

External skills are deliberately restrained rather than maximized.

The router selects only the product-design phases whose outputs are missing or
stale. External additions are phase specialists, not aesthetic authority:

- discovery/strategy skills from trusted design collections;
- UI UX Pro Max, Taste Skill, or Impeccable for the appropriate phase;
- shadcn, 21st.dev, Aceternity, or Figma tooling for components/translation;
- Vercel framework guidance for engineering and audit quality;
- Anthropic `frontend-design` only as optional supplementary design intelligence.

Run:

```bash
./scripts/install-skills.sh
```

The principle:

> Install narrow, relevant expertise. Do not load a hundred overlapping skills and hope the agent chooses correctly.

> References are ingredients. Components are structural donors. Tokens encode
> approved decisions. The project design system wins.

For design-critical work, `design-intake` asks only the relevant brand, palette,
type, density, geometry, motion, platform, and accessibility questions. It then
compares realistic directions and requires human approval before changing the
canonical design system or tokens.

### Activate only what the project needs

The starter catalogs web, mobile, backend, research, and design capabilities,
but `.agentic/project.json` determines which profiles are active.

```bash
./scripts/init-project.sh
./scripts/profile-resolve.sh
./scripts/profile-doctor.sh
./scripts/profile-preview.sh web-next,design-critical,research-enabled
```

Profile selection is non-destructive: it does not silently install tools or
delete inactive surfaces.

The guided initializer asks what you are building, previews the resulting
profiles, clearly lists what stays inactive, and changes only
`.agentic/project.json` after confirmation.

```bash
./scripts/init-project.sh --list-presets
./scripts/init-project.sh --name my-saas --preset web-supabase --dry-run
```

If you choose web without mobile, mobile agents and guidance stay inactive.
Nothing is installed or deleted automatically, so profile selection remains
safe and reversible.

![Actual non-destructive project profile preview](docs/assets/demo/01-project-profiles.gif)

### Turn a task into a safe workspace

```bash
./scripts/task-plan.sh T-009
./scripts/task-start.sh T-009 --yes
```

The planner checks dependencies, active profiles, agent routing, exclusive file
ownership, and verification gates. Starting requires confirmation and creates a
short-lived branch or isolated worktree; it does not implement or merge the
task.

This is the real read-only planner running against the completed Signalroom
showcase task, `T-007`:

![Actual task planner output for Signalroom task T-007](docs/assets/demo/02-task-plan.gif)

See the complete
[product-design resource catalog](docs/60-tooling/PRODUCT_DESIGN_RESOURCES.md)
for source links, commands, phase routing, usage guidance, and original
assessments.

---

## MCP stack

The project includes three core MCP capabilities.

### 🔎 Perplexity

For:

- Current web research
- Source discovery
- Deep research
- Web-grounded questions
- Reasoning over current information

Official project: https://github.com/perplexityai/modelcontextprotocol

---

### 🔥 Firecrawl

For:

- Scraping exact URLs
- Mapping websites
- Crawling documentation or site sections
- Structured extraction
- Research-heavy workflows

Official project: https://github.com/firecrawl/firecrawl-mcp-server

---

### 🎭 Microsoft Playwright MCP

For:

- Browser interaction
- UI verification
- Forms and workflows
- JavaScript-heavy applications
- Accessibility inspection
- Visual QA
- Authenticated journeys
- Exploratory browser automation

The starter uses isolated browser sessions by default.

Official project: https://github.com/microsoft/playwright-mcp

---

### MCP routing philosophy

```text
Need broad, current web research?
    → Perplexity

Know the exact URL?
    → Firecrawl scrape

Need to discover pages on a site?
    → Firecrawl map

Need an entire documentation site or section?
    → Firecrawl crawl with explicit limits

Need structured fields from web content?
    → Firecrawl extraction

Need clicks, forms, login, browser state, or actual UI interaction?
    → Playwright
```

Use the right tool for the job instead of sending every problem through every MCP.

---

## Product development starts with traceability

A vague prompt should not become thousands of lines of code.

The system converts:

```text
IDEA
  ↓
PRODUCT INTERVIEW
  ↓
PRD
  ↓
STABLE REQUIREMENT IDs
  ↓
ACCEPTANCE CRITERIA
  ↓
ATOMIC TASKS
  ↓
IMPLEMENTATION
  ↓
TESTS
  ↓
EVIDENCE
```

Requirements use stable IDs:

```text
FR-001
FR-002
NFR-001
AC-001
AC-002
```

An executable task can trace directly back to product intent:

```json
{
  "id": "T-014",
  "title": "Build password reset confirmation state",
  "requirement_ids": ["FR-018"],
  "acceptance_ids": ["AC-041", "AC-042"],
  "owner": "frontend",
  "depends_on": ["T-009"],
  "status": "ready",
  "files_owned": [
    "apps/web/app/reset-password/**"
  ],
  "verification": [
    "unit",
    "e2e",
    "visual"
  ]
}
```

That creates traceability from:

> **Idea → Requirement → Acceptance Criterion → Task → Code → Test → Evidence**

---

## Parallel agents without merge chaos

Before write-heavy parallel work, the orchestrator defines:

1. Dependency DAG
2. File ownership matrix
3. Shared-state analysis
4. Worktree plan
5. Integration contracts
6. Merge order
7. Verification gates

Example:

```text
                    T-101
                API CONTRACT
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       T-102       T-103       T-104
       Backend        Web         Mobile
```

Instead of:

```text
Backend agent invents API A

Frontend agent expects API B

Mobile agent assumes API C

              ↓

       Integration chaos
```

For isolated parallel coding:

```bash
./scripts/create-worktree.sh T-014 password-reset agent main
```

Codex desktop can also create a dedicated managed worktree for each task. Use
one task, branch, and exclusive file owner per writing workspace. See the
[parallel terminals and Codex worktree guide](docs/70-collaboration/PARALLEL_TERMINALS.md).

---

## GitHub workflow for humans and agents

This repository includes a complete collaboration workflow:

```text
IDEA / BUG / REQUIREMENT
          ↓
    GITHUB ISSUE
      when warranted
          ↓
       TASK ID
          ↓
 SHORT-LIVED BRANCH
          ↓
 IMPLEMENT + VERIFY
          ↓
    DRAFT PR EARLY
      when useful
          ↓
 HUMAN + AGENT REVIEW
          ↓
 CI + SECURITY + CODEOWNERS
          ↓
 ACCEPTANCE CRITERIA PASS?
       │             │
      NO            YES
       │             │
      FIX      SQUASH MERGE
       │             │
       └─────────────┘
                     ↓
                    MAIN
                     ↓
              DELETE BRANCH
                     ↓
            RECORD DURABLE STATE
                     ↓
                 NEXT TASK
```

### Included GitHub assets

```text
.github/
├── workflows/
│   ├── ci.yml
│   ├── pr-policy.yml
│   ├── release.yml
│   └── showcase.yml
│
├── ISSUE_TEMPLATE/
│   ├── bug.yml
│   ├── feature.yml
│   ├── task.yml
│   └── config.yml
│
├── PULL_REQUEST_TEMPLATE.md
└── CODEOWNERS
```

Also included:

- Branch naming rules
- PR title enforcement
- Issue guidance
- Draft PR guidance
- Code review standards
- Team collaboration rules
- CODEOWNERS template
- Worktree utilities
- PR-readiness scripts
- Merge preparation
- Hotfix guidance
- Protected `main` recommendations

### Branch naming

```text
<type>/<TASK-ID>-<short-description>
```

Examples:

```text
feat/T-014-password-reset
fix/T-028-token-expiry
security/T-060-rate-limit
agent/T-014-password-reset
```

Create a branch:

```bash
./scripts/new-branch.sh feat T-014 password-reset
```

### PR naming

```text
<type>(<TASK-ID>): <imperative summary>
```

Examples:

```text
feat(T-014): add password reset confirmation
fix(T-028): prevent expired refresh token reuse
security(T-060): enforce request rate limiting
```

### Default merge strategy

**Squash merge.**

One coherent PR becomes one coherent commit on `main`.

Instead of:

```text
WIP
fix
oops
actually final
lint
final final
final final 2
```

You get:

```text
feat(T-014): add password reset confirmation (#128)
```

Read:

```text
docs/70-collaboration/GITHUB_WORKFLOW.md
```

---

## Product-design engine

Code is increasingly cheap. Product judgment, interaction quality, visual
coherence, and human-agent experience are not.

This starter treats design as a routed engineering discipline:

```text
DISCOVERY
→ USER NEEDS
→ BENCHMARK
→ UX STRATEGY
→ INTERACTION + AGENTIC UX
→ ADAPTIVE DESIGN INTAKE
→ DESIGN DIRECTIONS
→ HUMAN APPROVAL
→ DESIGN SYSTEM
→ DESIGN TOKENS
→ COMPONENT / FIGMA TRANSLATION
→ IMPLEMENTATION
→ LIVE ITERATION
→ RESPONSIVE / ACCESSIBILITY / SYSTEM / TOKEN AUDITS
→ PERFORMANCE
→ INDEPENDENT CRITIQUE
→ POLISH
→ DESIGN OPS
→ SHIP
```

`product-design-router` inspects the task and durable artifacts, then runs only
the phases that are missing or stale. A small fix does not repeat discovery. A
0→1 product does not skip it.

The intake adapts to the selected project profiles. A web-only project is not
asked about native mobile behavior; a restrained internal tool does not need
three expressive art directions; an existing brand supplies authoritative
colors and fonts rather than receiving guessed replacements.

The authority model is explicit:

```text
PRODUCT INTENT
→ RESEARCHED REFERENCES
→ APPROVED DESIGN BRIEF + DIRECTION
→ ORIGINAL VISUAL THESIS
→ DESIGN_SYSTEM.md
→ DTCG-COMPATIBLE TOKENS
→ COMPONENTS
→ RUNNING EXPERIENCE
```

- References are ingredients, not templates.
- Components from shadcn, 21st.dev, Aceternity, Figma, or other registries are
  structural donors—not the product identity.
- Tokens encode approved decisions; they never invent the direction.
- Anthropic `frontend-design` is optional supplementary intelligence, not the
  default art director.
- The project design system wins every conflict.

The builder cannot certify its own work. Playwright evidence, focused audits,
and an independent critic evaluate the running product before polish and ship.

### Design-token architecture

```text
PRIMITIVES
→ SEMANTIC TOKENS
→ SELECTIVE COMPONENT TOKENS
→ LIGHT / DARK THEMES
→ WEB / MOBILE OUTPUTS
```

The included DTCG-compatible scaffold covers color, typography, spacing,
radii, borders, elevation, motion, layout, density, components, themes, and
agent states such as thinking, running, approval, completion, and failure.

The token build also validates light/dark semantic parity and required contrast
pairs, resolves component tokens per mode, and generates a visual token specimen
alongside web and native outputs. This lets a redesign update approved
primitive/semantic mappings instead of restyling every screen independently.

---

## Security is enforced, not merely prompted

The starter includes deterministic security controls.

### Before tool execution

A `PreToolUse` hook blocks obvious destructive operations such as:

```text
git push --force
git reset --hard
terraform destroy
kubectl delete
package publishing
obvious production deployments
DROP DATABASE
DROP SCHEMA
DROP TABLE
recursive deletion from filesystem root
```

### After edits

The system checks edited files for likely:

```text
AWS credentials
GitHub tokens
private keys
hard-coded API keys
hard-coded passwords
hard-coded secrets
```

### Human approval is required for

- Production deployment
- Destructive database migration
- Credential changes
- Irreversible external actions
- Other explicitly high-risk operations

External content is treated as untrusted input, including:

- Web pages
- Crawled content
- GitHub issue comments
- MCP results
- Third-party documentation

Read:

```text
docs/30-engineering/SECURITY_MODEL.md
```

---

## Definition of done

A task is **not complete because an agent says it is complete**.

A task is complete only when:

1. Its linked requirements and acceptance criteria are identified.
2. The implementation exists.
3. Relevant tests pass.
4. UI work is visually inspected in the running product.
5. Security-sensitive changes pass security review.
6. Documentation reflects reality.
7. Durable state is updated when project state changes.
8. Evidence is recorded.
9. The task's PR is merged into `main`.

```text
"Implemented" ≠ "Done"

"Tests passed" ≠ always "Done"

"Agent says it works" ≠ evidence
```

Read:

```text
docs/50-evals/RUBRIC.md
```

The full repository verification below is executed rather than mocked. It
checks JSON/JSONL, GitHub workflows, profiles, the initializer, task routing,
design tokens, security hooks, documentation links, evidence bundles, lint,
types, and tests.

![Actual full repository verification](docs/assets/demo/05-verification.gif)

---

## Repository structure

```text
.
├── CLAUDE.md
├── AGENTS.md
├── CONTRIBUTING.md
├── .mcp.json
│
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
│
├── .claude/
│   ├── settings.json
│   ├── agents/
│   ├── rules/
│   ├── skills/
│   └── hooks/
│
├── .codex/
│   ├── config.toml
│   └── hooks.json
│
├── .agents/
│   └── skills -> ../.claude/skills
│
├── .codex-plugin/
│   └── plugin.json
│
├── skills -> .claude/skills
│
├── docs/                         # Open directly as an Obsidian vault
│   ├── 00-vision/
│   ├── 10-product/
│   ├── 20-design/
│   ├── 30-engineering/
│   ├── 40-execution/
│   ├── 50-evals/
│   ├── 60-tooling/
│   ├── 70-collaboration/
│   └── 90-archive/
│
├── apps/
│   ├── web/
│   └── mobile/
│
├── packages/
│   ├── api/
│   ├── config/
│   ├── database/
│   ├── design-tokens/
│   ├── domain/
│   ├── types/
│   └── ui/
│
└── scripts/
```

---

## Obsidian as the human cockpit

Open:

```text
docs/
```

directly as an Obsidian vault.

The model is simple:

```text
Git repository
    =
Machine-readable source of truth

docs/
    =
Shared human + agent knowledge

Obsidian
    =
Human interface over that knowledge

Git
    =
Durable history and checkpoints
```

You do not need a separate vector database just to stop losing project context.

Start with version-controlled Markdown.

Add more infrastructure only when a real limitation appears.

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/Gaurav890/everything-agentic-engineering.git
cd everything-agentic-engineering
```

### 2. Choose the project capabilities

```bash
./scripts/init-project.sh
```

This does not install or remove anything. Review the proposed manifest, then
run:

```bash
./scripts/profile-doctor.sh
```

### 3. Configure environment

```bash
cp .env.example .env
```

Add the API keys for the MCP services you plan to use.

### 4. Bootstrap

```bash
./scripts/bootstrap.sh
```

### 5. Check your MCP setup

```bash
./scripts/mcp-doctor.sh
```

### 6. Verify the harness

```bash
./scripts/verify.sh full
```

This runs profile and initializer tests, token generation, security-hook tests,
Codex adapter drift tests, documentation-link checks, policy checks, and
project-defined checks.

### 7. Open your coding agent

Claude Code:

```bash
claude
```

Codex:

```bash
./scripts/codex-doctor.sh
codex
```

Codex reads `AGENTS.md` and discovers the same local skills through
`.agents/skills`. The committed adapter does not select a model, widen
permissions, configure credentials, or start external MCP servers. Read the
[Codex adapter guide](docs/60-tooling/CODEX.md).

It also discovers seven project-scoped, read-only specialist roles for product
planning, architecture, research, design critique, security review, QA, and
integration review. Use these subagents for parallel analysis; use separate
task worktrees—not writable in-session subagents—for parallel implementation.

### 8. Start with an idea

Try:

```text
I want to build a SaaS product for independent restaurants to track,
understand, and reduce food waste.

Start by reading CLAUDE.md.

Interview me to understand the problem, target user, workflows,
constraints, edge cases, business model, security considerations,
and success criteria.

Then create the PRD with stable requirement IDs and acceptance criteria.

Do not implement anything until the PRD and implementation plan
have been reviewed and approved.
```

Then move from:

```text
IDEA
  ↓
DISCOVERY + USER NEEDS
  ↓
PRD + ACCEPTANCE CRITERIA
  ↓
UX STRATEGY + INTERACTION MODEL
  ↓
DESIGN SYSTEM + TOKENS
  ↓
ARCHITECTURE
  ↓
TASK DAG
  ↓
IMPLEMENTATION
  ↓
RUNNING-PRODUCT AUDITS + INDEPENDENT CRITIQUE
  ↓
PULL REQUEST
  ↓
MERGE
```

---

## Project profiles

Profiles are composable decisions, not one oversized default:

| Profile | Activates |
|---|---|
| `core` | Durable context, tasks, verification, and collaboration |
| `web-next` | Next.js surface, frontend owner, React guidance, Playwright |
| `mobile-expo` | Expo surface, mobile owner, React Native guidance |
| `design-critical` | Product-design router, tokens, and running-UI evidence |
| `research-enabled` | Researcher, source ledger, Perplexity, Firecrawl, Playwright |
| `backend-supabase` | Supabase as the selected backend |
| `backend-convex` | Convex as the selected backend |

Supabase and Convex conflict by design. Web does not imply mobile; mobile does
not imply web; neither app surface implies research. The guided initializer
selects only the required composition and explains what remains inactive.

Read:

```text
docs/60-tooling/PROFILES.md
```

---

## What this is not

This is **not**:

- A list of 500 random agents.
- A dump of 200 overlapping skills.
- A folder containing clever prompts.
- A replacement for engineering judgment.
- A promise that autonomous agents never make mistakes.
- An excuse to skip code review.
- An excuse to give an agent production credentials.
- A magic button that turns vague ideas into perfect software.

It is an opinionated system for making agentic software development more structured, durable, collaborative, testable, and accountable.

---

## Philosophy

A few rules drive the entire project:

> **The conversation is disposable. The repository is durable memory.**

> **Parallelize independent outputs, not shared state.**

> **One agent builds. Another evaluates.**

> **Evidence beats confidence.**

> **Skills provide expertise. Agents own responsibility. MCPs provide capabilities. Hooks enforce rules.**

> **A task is not done until reality agrees.**

---

## Roadmap

Potential future directions:

- [x] Interactive project initializer CLI with safe presets and previews
- [x] Selectable web, mobile, backend, design, and research profiles
- [x] Reviewed branch/worktree creation from `TASKS.jsonl`
- [ ] Deeper GitHub Issue ↔ Task synchronization
- [ ] Agent-team orchestration examples
- [x] Visual regression pipeline for the Showcase's required states
- [ ] Security scanner integrations
- [ ] Additional evaluation patterns
- [x] Codex-native instructions, shared skills, hooks, doctor, and plugin manifest
- [x] Codex-specific read-only subagent role adapters
- [ ] Example production application built entirely with the harness
- [ ] Community-contributed skills, agents, and project profiles

Have an idea? Open an issue or start a discussion.

For maintainers, see the [release runbook](docs/70-collaboration/RELEASING.md).
For launch material, see the [copy deck](docs/80-showcase/LAUNCH_COPY.md).

---

## Contributing

Contributions are welcome.

Please read:

```text
CONTRIBUTING.md
docs/70-collaboration/GITHUB_WORKFLOW.md
docs/70-collaboration/CODE_REVIEW.md
```

You can contribute through:

- Bug reports
- Feature proposals
- Documentation improvements
- New skills
- Agent improvements
- Evaluation strategies
- Security improvements
- Project profiles
- Real-world examples

Please do not submit enormous unrelated changes in one PR.

Small, focused, well-evidenced contributions are easier to review and merge.

---

## Support the project

If this project helps you build better software with coding agents:

⭐ **Star the repository**

🍴 **Fork it and adapt it to your workflow**

🧪 **Test it on a real project**

🐛 **Open issues when something breaks**

🔀 **Submit focused pull requests**

📢 **Share what worked and what did not**

The goal is not to create the biggest collection of agent tooling.

The goal is to build a better engineering system for humans and agents working together.

---

<div align="center">

## Stop giving coding agents prompts. Give them an engineering system.

**Everything Agentic Engineering**

[⭐ Star](https://github.com/Gaurav890/everything-agentic-engineering) ·
[🐛 Issues](https://github.com/Gaurav890/everything-agentic-engineering/issues) ·
[🔀 Contribute](CONTRIBUTING.md)

</div>
