---
name: codex-adapter
description: Validate and operate Everything Agentic Engineering with Codex. Use when configuring Codex for this repository, checking AGENTS.md or skill discovery, preparing parallel Codex worktrees, packaging the repository plugin, reviewing Codex hooks, or diagnosing Claude/Codex contract drift.
---

# Codex adapter

## Establish the runtime contract

1. Read `AGENTS.md`, `.agentic/project.json`, the active task, and
   `docs/60-tooling/CODEX.md`.
2. Run `./scripts/codex-doctor.sh` before changing Codex-specific files.
3. Treat `AGENTS.md` as the cross-runtime constitution. Treat `.codex/` as the
   Codex adapter and `.claude/` as the canonical local skill and safety-script
   source.
4. Do not add model selection, credentials, provider routing, network access,
   MCP servers, sandbox expansion, or approval bypasses without an explicit,
   separately reviewed requirement.

## Route work safely

- Use the local checkout for orchestration or one foreground task.
- Use one branch and worktree per independent write-heavy task.
- Assign exclusive file or tightly coupled module ownership before parallel
  work starts.
- Merge shared contracts before dependent implementations.
- Keep the final evaluator separate from the builder.

Use `./scripts/task-plan.sh <TASK-ID>` before workspace creation and follow
`docs/70-collaboration/PARALLEL_TERMINALS.md` for multi-terminal work.

## Maintain the adapter

- Keep `.agents/skills` and the plugin `skills` path pointed at the canonical
  `.claude/skills` tree; do not create hand-maintained copies.
- Keep `.codex/hooks.json` wired to the reviewed scripts under
  `.claude/hooks/`.
- Validate changes with `./scripts/codex-doctor.sh`, the skill validator, the
  plugin validator, and `./scripts/verify.sh full`.
- Update compatibility documentation when a runtime floor or limitation
  changes.

Read [references/contract.md](references/contract.md) when changing adapter
files, packaging, or acceptance criteria.
