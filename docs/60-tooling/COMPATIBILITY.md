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

`v0.1.x` is the first public preview line. Until `v1.0.0`, profile manifests,
token formats, task schemas, and durable contracts may evolve between minor
versions. Breaking changes must still be called out in the changelog and
include a migration note.

## Known limitations in v0.1.0

- Signalroom is a static reference experience, not a connected agent runtime.
- Project profiles route and validate capabilities; they do not install or
  remove inactive template inventory.
- Optional external skills and MCP servers remain separately installed and may
  require their own accounts or API keys.
- Windows is supported through WSL on a best-effort basis; native PowerShell
  wrappers are not included.
- Figma, GitHub repository settings, social previews, tags, releases, and
  production deployments remain explicit human actions.
- The research loop may propose updates but cannot adopt, commit, merge, or
  release them autonomously.

See the [v0.1.0 release notes](../releases/v0.1.0.md) for the exact public
preview scope.
