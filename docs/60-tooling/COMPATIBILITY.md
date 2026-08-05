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

## Claude Code runtime notes

The repository does not silently pin or upgrade Claude Code. Runtime behavior
must be checked against the installed version.

- Claude Code 2.1.217 introduced a default concurrent-subagent cap; 2.1.219
  changed the default nested-spawn depth to three. Projects that require a
  non-nested topology may set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` only
  after a maintainer approves the runtime policy.
- Claude Code 2.1.221 or newer is recommended for Linux/WSL workflows that make
  credential files available to sandboxed commands or rely on zsh permission
  analysis. That release adds credential-file masking on Linux/WSL and fixes a
  zsh permission-check bypass. On macOS the masking mode falls back to denial.
- This recommendation does not authorize adding credential paths, secrets,
  sandbox settings, or network allowlists to the repository. Inventory and
  approve those separately.

See `LEARNING_LEDGER.md` for dated primary-source evidence and uncertainty.

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
