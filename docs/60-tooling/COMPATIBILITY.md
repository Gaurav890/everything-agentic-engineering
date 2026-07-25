# Compatibility

## Supported baseline

| Surface | Status | Notes |
|---|---|---|
| macOS | Supported | Primary development environment |
| Linux / GitHub Actions | Supported | Full verification runs on Ubuntu |
| Windows | Best effort | Use WSL until PowerShell wrappers exist |
| Claude Code | Supported | Native `.claude/` agents, rules, skills, and hooks |
| Codex | Supported by contract | `AGENTS.md` plus skill metadata where provided |
| Other coding agents | Adaptable | Must honor repository source-of-truth and safety contracts |

## Profiles

Profiles describe required capabilities; they do not silently install them.
Run `./scripts/profile-doctor.sh` after tool or agent upgrades.

## Versioning

Before the first tagged release, `main` is the supported line. After `v1.0.0`,
breaking changes to profile manifests, token formats, task schemas, or durable
contracts require a major version or a documented migration.
