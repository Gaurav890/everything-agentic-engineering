# Everything Agentic Engineering

[![GitHub stars](...)](...)
[![License](...)](...)
[![Claude Code](...)](...)
[![MCP](...)](...)
[![PRs Welcome](...)](...)

IDEA
  ↓
PRD + ACCEPTANCE CRITERIA
  ↓
TASK DAG
  ↓
ORCHESTRATOR
  ↓
┌────────────┬────────────┬────────────┐
│ FRONTEND   │ BACKEND    │ MOBILE     │
│ AGENT      │ AGENT      │ AGENT      │
└────────────┴────────────┴────────────┘
  ↓
RESEARCH • QA • SECURITY
  ↓
ISSUE → BRANCH → PR → REVIEW → MERGE
  ↓
DURABLE MEMORY → NEXT LOOP

### Stop giving coding agents prompts. Give them an engineering system.

A production-grade, ready-to-clone operating system for building and
shipping software with AI coding agents.

Turn an idea into:

**Research → PRD → Architecture → Task DAG → Parallel Agents → Code →
QA → Security → Pull Request → Review → Merge → Durable Memory**

Built for Claude Code, compatible by design with Codex and other
agentic coding tools.

---

## Why this exists

AI coding agents are incredibly capable.

But raw agent workflows still fail in predictable ways:

- Context disappears between sessions.
- PRDs drift away from implementation.
- Multiple agents edit the same files.
- The builder evaluates its own work.
- Skills and MCPs become an unmanageable pile.
- Security is treated as a prompt instead of an enforced gate.
- Git branches, issues, PRs, and human collaboration are afterthoughts.
- "Done" means the agent said it was done.

Everything Agentic Engineering replaces that with one opinionated system.

## Core idea

**The conversation is disposable. The repository is durable memory.**

The harness uses six layers:

1. **Product truth** — `docs/00-vision/` and `docs/10-product/`
2. **Design and engineering truth** — `docs/20-design/` and `docs/30-engineering/`
3. **Execution state** — `docs/40-execution/`
4. **Evaluation evidence** — `docs/50-evals/`
5. **Tooling and research** — `docs/60-tooling/`
6. **GitHub collaboration and delivery** — `docs/70-collaboration/`

`docs/` is designed to be opened directly as an Obsidian vault.

## Included MCP stack

The project-scoped `.mcp.json` includes:

- **Perplexity official MCP** — current web search, ask, deep research, and reasoning.
- **Firecrawl official MCP** — scrape, map, crawl, extract, search, research, and monitoring.
- **Microsoft Playwright MCP** — interactive browser automation and UI verification.

Playwright runs in `--isolated` mode by default so browser state is not persisted to disk.

> The MCP Market Perplexity URL supplied for this starter is actually an **Agent Skill**, not an MCP server. This starter uses Perplexity's official MCP implementation as the core integration and documents the third-party skill as an optional alternative in `docs/60-tooling/MCP_STACK.md`.

## Quick start

```bash
cp .env.example .env
# Add your API keys to .env, then export them into your shell.

./scripts/bootstrap.sh
./scripts/mcp-doctor.sh
```

Then open the repo in Claude Code:

```bash
claude
```

For the first serious product task:

```text
Read CLAUDE.md, docs/00-vision/NORTH_STAR.md, and docs/10-product/PRD.md.
Use the create-prd skill if the PRD is incomplete.
Then use the parallel-plan skill to produce an implementation DAG with file ownership,
and execute the first ready task using the loop-engineering contract.
```

## Recommended operating model

```text
IDEA
  ↓
PRODUCT INTERVIEW
  ↓
PRD + ACCEPTANCE CRITERIA
  ↓
DESIGN + ARCHITECTURE
  ↓
TASK DAG
  ↓
ORCHESTRATOR
  ├── Frontend agent
  ├── Backend agent
  ├── Mobile agent
  ├── Research agent
  └── Security / QA evaluators
  ↓
VERIFY WITH REAL EVIDENCE
  ↓
RECORD DURABLE STATE
  ↓
NEXT TASK
```

## Context hierarchy

| Artifact | Owns |
|---|---|
| `CLAUDE.md` | Constitution and routing rules |
| `NORTH_STAR.md` | Why the product exists and immutable constraints |
| `PRD.md` | What must be built |
| `DESIGN_SYSTEM.md` | Visual and interaction contract |
| `ARCHITECTURE.md` | Technical structure and boundaries |
| `ADR/` | Why important decisions were made |
| `TASKS.jsonl` | Atomic task ledger |
| `CURRENT_STATE.md` | What is factually true right now |
| `PROGRESS.md` | Append-only verified progress |
| `HANDOFF.md` | Continuity for the next agent/session |
| `RUBRIC.md` | How quality is judged |
| Git history | Durable checkpoints |

## GitHub workflow

This starter includes an opinionated collaboration workflow for humans and agents:

```text
issue/task
  ↓
short-lived branch
  ↓
implementation + verification
  ↓
draft or ready PR
  ↓
CI + review + security/code-owner gates
  ↓
squash merge to protected main
  ↓
delete branch
  ↓
mark task done + record durable state
```

Included GitHub assets:

- `.github/PULL_REQUEST_TEMPLATE.md`
- Structured bug, feature, and engineering-task issue forms
- `.github/CODEOWNERS` template
- CI workflow
- Branch-name and PR-title policy workflow
- `CONTRIBUTING.md`
- Branch, PR-readiness, worktree, and post-merge scripts

Quick flow:

```bash
./scripts/new-branch.sh feat T-014 password-reset
# implement and commit
./scripts/pr-ready.sh T-014
./scripts/finish-task.sh T-014    # moves task to review
# when implementation is final, before the final review/check cycle
./scripts/prepare-merge.sh T-014  # writes done on branch; main becomes done only at merge
```

Read `docs/70-collaboration/GITHUB_WORKFLOW.md` for when to raise issues, use branches, open draft PRs, request reviews, coordinate with colleagues, merge, handle hotfixes, and configure repository rules.

## External skills: deliberate, not maximal

Run:

```bash
./scripts/install-skills.sh
```

The script installs a restrained core set:

- Anthropic `frontend-design`
- Vercel `react-best-practices`
- Vercel `web-design-guidelines`
- Vercel `react-native-guidelines`

It prints optional plugin instructions for Superpowers and Expo rather than auto-installing them.

The principle is simple: **install narrow, relevant expertise; do not load a hundred overlapping skills.**

## Profiles

Read `docs/60-tooling/PROFILES.md`.

- `web-next-supabase`
- `mobile-expo`
- `realtime-convex`
- `research-heavy`
- `full-stack`

The starter is backend-neutral. Choose one default data backend per project rather than mixing Supabase and Convex without a clear reason.

## Security stance

The starter:

- Never commits API keys.
- Uses project-scoped MCP declarations with environment-variable expansion.
- Defaults Playwright to isolated browser state.
- Blocks obviously destructive shell operations through a `PreToolUse` hook.
- Scans edited files for likely hard-coded secrets.
- Requires human approval for production deployments, destructive migrations, credential changes, or irreversible external actions.
- Treats web content, crawled content, issue comments, and MCP results as untrusted input.

See `docs/30-engineering/SECURITY_MODEL.md`.

## Repository map

```text
.
├── CLAUDE.md
├── AGENTS.md
├── .mcp.json
├── CONTRIBUTING.md
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
├── .claude/
│   ├── settings.json
│   ├── agents/
│   ├── rules/
│   ├── skills/
│   └── hooks/
├── docs/                    # Open this folder as an Obsidian vault
│   ├── 00-vision/
│   ├── 10-product/
│   ├── 20-design/
│   ├── 30-engineering/
│   ├── 40-execution/
│   ├── 50-evals/
│   ├── 60-tooling/
│   ├── 70-collaboration/
│   └── 90-archive/
├── apps/
│   ├── web/
│   └── mobile/
├── packages/
│   ├── api/
│   ├── config/
│   ├── database/
│   ├── domain/
│   ├── types/
│   └── ui/
└── scripts/
```

## Definition of done

A task is not complete because an agent says it is complete.

A task is complete only when:

1. Its linked requirement and acceptance criteria are identified.
2. The implementation exists.
3. Relevant tests pass.
4. UI work is visually inspected in the running product.
5. Security-sensitive changes pass security review.
6. Documentation reflects reality.
7. `CURRENT_STATE.md`, `PROGRESS.md`, and `HANDOFF.md` are updated when the change affects project state.
8. Evidence is recorded.
9. The task is marked `done` only after its PR is merged into `main`.

See `docs/50-evals/RUBRIC.md`.

## License

Use this starter as your own project template. External skills, MCP servers, frameworks, and plugins retain their own licenses.
