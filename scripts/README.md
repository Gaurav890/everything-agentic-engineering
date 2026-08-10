# Command architecture

Use the root `./agentic` command for contributor workflows. Run
`./agentic --help` for the grouped command surface or
`./agentic commands --json` for machine-readable discovery.

The canonical registry is [`.agentic/commands.json`](../.agentic/commands.json).
It owns:

- the supported public command paths;
- their current implementation targets and impact classification;
- the complete shell-file inventory;
- the separation between public commands, internal policy helpers,
  compatibility adapters, and security hooks.

## Boundaries

| Classification | Meaning |
|---|---|
| `public` | Supported workflow exposed through `./agentic` |
| `internal` | Invoked by CI or another supported workflow; not a user command |
| `compatibility` | Retained for existing callers while a replacement is established |
| `security_hook` | Invoked directly by an agent runtime; never routed through the CLI |

The CLI dispatches an argument list directly to a registered script. It never
uses shell-string evaluation. Registry targets must remain inside `scripts/`.
Security hooks remain directly wired through `.claude/settings.json` and
`.codex/hooks.json` so a convenience layer cannot bypass them.

## Compatibility and cleanup policy

Phase one is additive. Existing `./scripts/*.sh` invocations remain supported
so downstream repositories, documentation links, and CI do not break.

A later removal requires all of the following:

1. the replacement has shipped in a tagged release;
2. primary documentation and CI use `./agentic`;
3. repository search finds no unsupported internal callers;
4. a deprecation notice and migration path exist;
5. release-smoke and full verification pass after removal;
6. human review explicitly approves the deletion.

Do not move or delete scripts merely to make the directory look smaller. The
goal is a smaller mental model for contributors and agents, with compatibility
removed only when evidence says it is safe.
