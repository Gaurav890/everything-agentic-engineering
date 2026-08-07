# Codex adapter contract

## Authority

| Concern | Authority |
|---|---|
| Cross-runtime workflow and safety | `AGENTS.md` |
| Codex project behavior | `.codex/config.toml` |
| Codex lifecycle wiring | `.codex/hooks.json` |
| Canonical local skills | `.claude/skills/` |
| Codex repository discovery | `.agents/skills` |
| Plugin skill packaging | `skills` and `.codex-plugin/plugin.json` |
| Parallel execution | task ledger and collaboration documentation |

Both `skills` links must resolve to `.claude/skills`; drift is a verification
failure.

## Safe project configuration

The committed Codex configuration may set repository instruction size,
bounded agent concurrency, and lifecycle-hook discovery. It must not select a
model or provider, define credentials, register external MCP execution, enable
network access, weaken a sandbox, or bypass approval.

User, workspace-admin, and managed policy remain authoritative. Project hooks
run only after Codex trust review.

## Acceptance criteria

- Codex discovers `AGENTS.md` and the shared local skills.
- Claude continues to discover the unchanged `.claude/skills` paths.
- The plugin manifest validates against the current plugin schema.
- The project hook configuration invokes the reviewed shared safety scripts.
- A missing or older Codex runtime produces an actionable doctor warning; it
  does not break framework-independent CI.
- Strict runtime validation fails when the installed Codex version is below
  the documented plugin baseline.
- No committed adapter file grants additional external authority.
