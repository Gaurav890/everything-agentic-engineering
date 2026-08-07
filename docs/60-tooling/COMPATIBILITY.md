# Compatibility

## Supported baseline

| Surface | Status | Notes |
|---|---|---|
| macOS | Supported | Primary development environment |
| Linux / GitHub Actions | Supported | Full verification runs on Ubuntu |
| Windows | Best effort | Use WSL until PowerShell wrappers exist |
| Claude Code | Supported | Native `.claude/` agents, rules, skills, and hooks |
| Codex | Native adapter | `AGENTS.md`, shared repo skills, trusted project config/hooks, doctor, and skills-only plugin manifest |
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
- Claude Code 2.1.222 or newer is recommended for every workflow that relies on
  worktree isolation, background agents, `PreToolUse` auto-allow hooks, or
  cross-session messaging. That release closes isolation and permission gaps
  across those paths and prevents repository-local settings from enabling
  Remote Control.
- Claude Code 2.1.223 or newer is recommended when shell permission analysis,
  workflow agents, dynamic workflow imports, or managed bypass-permission
  policy are part of the trust boundary. That release closes additional command
  concealment, approval-dialog, workflow-sandbox, and organization-policy gaps.
- This recommendation does not authorize adding credential paths, secrets,
  sandbox settings, or network allowlists to the repository. Inventory and
  approve those separately.

See `LEARNING_LEDGER.md` for dated primary-source evidence and uncertainty.

## Codex runtime notes

The repository contract remains authoritative regardless of runtime defaults.

- Codex 0.146.1 or newer is the preferred stable baseline when using models
  identified by Codex as cyber-specialized. It applies safer review defaults
  and explains permission changes in the terminal.
- Codex 0.147.0 or newer is the recommended baseline for the repository's
  plugin workflow. `codex-doctor.sh --strict-runtime` enforces that floor on a
  developer machine; normal CI validates the adapter without installing or
  upgrading Codex.
- Do not infer authorization from an automatic reviewer or model default.
  Project permission profiles, human approval, security review, and external
  action boundaries still apply.
- The repository does not silently select models, enable automatic review, or
  expand filesystem, network, or external-service permissions.
- Project Codex configuration intentionally omits models, providers,
  credentials, MCP execution, sandbox selection, network access, writable-root
  expansion, and approval policy. User and managed enterprise policy remain
  authoritative.

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
- Claude agent definitions are not yet translated into Codex-specific subagent
  role files; Codex currently shares the repository contract, skills, hooks,
  worktree workflow, and plugin metadata.
- The Codex plugin manifest is package-ready but marketplace publication and
  installation policy remain explicit release actions.

See the [v0.1.0 release notes](../releases/v0.1.0.md) for the exact public
preview scope.
