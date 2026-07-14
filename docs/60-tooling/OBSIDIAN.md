# Obsidian setup

Open `docs/` as the Obsidian vault.

## Why

- Humans get links, graph view, search, templates, and readable notes.
- Agents get plain Markdown in the repository.
- Git provides durable history.
- No separate memory database is required for core project truth.

## Rules

- Do not open your entire personal Obsidian vault to autonomous coding agents by default.
- Keep project truth inside this repo.
- Add outside personal knowledge intentionally and with narrow scope.
- Do not store secrets in the vault.
- Prefer stable IDs and wiki links.

## Suggested graph

```text
NORTH_STAR
   ↓
PRD
   ↓
ACCEPTANCE_CRITERIA
   ↓
TASKS
   ↓
PROGRESS / EVIDENCE
   ↓
CURRENT_STATE / HANDOFF
```

## Optional Obsidian-specific skills

Only add Obsidian-specific agent skills when you need richer vault behavior such as Canvas, Bases, backlinks, or specialized vault operations. Plain Markdown is enough for the core workflow.
