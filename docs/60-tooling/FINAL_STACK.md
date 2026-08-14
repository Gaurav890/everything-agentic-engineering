# Final stack decision

This is the opinionated default for the reusable starter.

## Harness

- Claude Code and Codex adapters over one repository contract
- Git + GitHub
- `AGENTS.md` as the cross-runtime contract
- `CLAUDE.md` as the Claude project constitution
- `.claude/rules/` for scoped policies
- `.claude/skills/` as the canonical repeatable workflow catalog
- `.agents/skills` for Codex repository discovery without copied skills
- `.codex/` for safe Codex project configuration and hook wiring
- root `plugin.json` and `skills/` for the Agent Plugins 1.0 portable core
- `.codex-plugin/` for separate Codex-native compatibility metadata during the
  additive migration
- `.claude/agents/` for specialized roles
- hooks for deterministic guardrails
- Git worktrees for parallel write-heavy work
- `docs/` as the durable source of truth and Obsidian vault

## Core MCPs

1. **Perplexity official MCP**
   - current search
   - source discovery
   - deep research
   - reasoning

2. **Firecrawl official MCP**
   - scrape
   - map
   - crawl
   - extract
   - site research/monitoring

3. **Microsoft Playwright MCP**
   - interactive browser automation
   - JS-heavy flows
   - UI acceptance evidence
   - exploratory/long-running browser loops

### Final note on the supplied Perplexity MCP Market URL

That exact URL is an Agent Skill using Perplexity Sonar through OpenRouter/LiteLLM, not an MCP server.

Default decision:
- use the official Perplexity MCP in the core stack;
- keep the MCP Market skill optional, not duplicated by default.

## Core project-local skills

- create-prd
- decompose-prd
- context-handoff
- product-design-router
- discover
- user-needs
- benchmark
- strategize
- interaction-design
- agentic-ux
- design-system
- design-tokens
- responsive-audit
- accessibility-audit
- design-system-audit
- token-audit
- performance-ux
- design-critic
- polish
- design-ops
- research-ledger
- parallel-plan
- loop-engineering
- security-gate
- self-improvement-loop
- codex-adapter

## External skills

Install only when the active design phase needs them:

- discovery/strategy specialists;
- UI UX Pro Max, Taste Skill, or Impeccable phase tools;
- shadcn/21st.dev/Aceternity component discovery;
- Figma MCP/Code Connect for approved design translation;
- Vercel React/Next.js or React Native engineering guidance;
- Anthropic frontend-design as optional supplementary design intelligence.

Optional:
- Superpowers workflow plugin
- Expo official plugin for mobile
- one relevant creative/critique specialist at a time

The project design system is authoritative. References are ingredients,
components are structural donors, and tokens encode approved decisions.

## Web default

- Next.js
- TypeScript
- Tailwind
- shadcn/ui when useful
- Playwright
- Supabase as the default backend profile

## Mobile default

- Expo
- React Native
- TypeScript
- Expo Router
- official Expo skills/plugin
- Vercel react-native-guidelines

## Realtime alternative

Use Convex instead of Supabase when real-time reactive state is central.

Do not use Supabase and Convex together by default.

## Research routing

- current/broad/deep research → Perplexity
- exact page/site extraction → Firecrawl
- interactive browser behavior → Playwright
- framework docs → official docs first; Context7 optional

## Agent model

Default:
- main session acts as orchestrator
- specialists are invoked only when their domain is relevant
- evaluators are separate from builders
- parallel write-heavy work gets isolated worktrees
- one owner per file/module at a time

## Context model

- `NORTH_STAR.md` = why
- `PRD.md` = what
- `DESIGN_SYSTEM.md` = visual contract
- `ARCHITECTURE.md` = how
- `TASKS.jsonl` = executable work
- `CURRENT_STATE.md` = current truth
- `PROGRESS.md` = verified history
- `HANDOFF.md` = continuity
- `ADR/` = durable decisions
- Git = checkpoints

## Non-negotiable completion rule

A task is complete only when acceptance criteria are verified with real evidence and durable state is updated.

Agent confidence is never sufficient evidence.
