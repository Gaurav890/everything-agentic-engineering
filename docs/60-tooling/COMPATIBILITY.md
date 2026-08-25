# Compatibility

## Supported baseline

| Surface | Status | Notes |
|---|---|---|
| macOS | Supported | Primary development environment |
| Linux / GitHub Actions | Supported | Full verification runs on Ubuntu |
| Windows | Best effort | Use WSL until PowerShell wrappers exist |
| Claude Code | Supported | Native `.claude/` agents, rules, skills, and hooks |
| Codex | Native adapter | `AGENTS.md`, shared repo skills, trusted project config/hooks, doctor, and separate Codex-native manifest |
| Agent Plugins 1.0 | Portable skills-only core | Root `plugin.json` plus fixed `skills/`; portable MCP packaging is machine-blocked pending credential, execution, protocol, and clean-client evidence |
| Other coding agents | Adaptable | Must honor repository source-of-truth and safety contracts |

## Profiles

Profiles describe required capabilities; they do not silently install them.
Run `./scripts/profile-doctor.sh` after tool or agent upgrades.

## Runtime compatibility policy

`.agentic/runtime-baselines.json` is the machine-readable source for tested
Claude Code and Codex version floors and optional capability gates.

Run the read-only doctor after cloning or changing either runtime:

```bash
./scripts/runtime-doctor.sh
```

Advisory mode warns when a runtime is missing or below the recommended floor
without making portable repository CI depend on a local installation.
Enterprise validation can fail closed:

```bash
./scripts/runtime-doctor.sh --strict
./scripts/runtime-doctor.sh --json
```

The doctor never installs, upgrades, enables, authenticates, or configures a
runtime. A compatible version is a prerequisite, not authorization to enable
an optional capability.

In the manifest, `default_enabled: true` on a hardening or runtime-behavior
record describes behavior present at the tested upstream baseline; it is not
repository authorization for a new action. Authority-expanding optional
capabilities use `default_enabled: false` plus
`human_approval_required: true` and remain unavailable until separately
reviewed.

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
- Claude Code 2.1.224 or newer is recommended when filesystem deny rules,
  self-hosted environments, archive plugin sources, credential extraction, or
  cross-session messaging are being evaluated. That release fixes trailing-
  slash filesystem deny entries and introduces those optional surfaces.
- Claude Code 2.1.228 hardens skills synced from claude.ai so they cannot shadow
  local commands or MCP prompts, sanitizes and labels their descriptions, and
  prevents their local bodies from running shell directives or expanding file
  imports. Synced or third-party skills remain untrusted inputs until reviewed.
- Claude Code 2.1.229 adds server-supplied hooks for self-hosted sessions and
  dynamically resolved plugin marketplace command sources. Those authority-
  expanding surfaces remain optional. The same release fails ambiguous IPv6
  sandbox rules closed and stops `/commit-push-pr` from auto-approving dangerous
  Git flags.
- Claude Code 2.1.231 fixes OAuth redirect handling for MCP servers that use a
  pre-registered client. This does not enable or authenticate an MCP server.
- Claude Code 2.1.232 turns forked-subagent context inheritance on by default
  and runs non-teammate interactive spawns in the background by default. The
  repository still keeps in-session specialists read-only, isolates writers
  in branches/worktrees, and requires the orchestrator to await and evaluate
  results.
- The 2.1.232 baseline also includes PowerShell permission fixes,
  per-repository trust for nested repositories, shared-socket and Linux sandbox
  hardening, protection against project-level sandbox binary overrides, and
  managed approval for server-supplied sandbox binary changes.
- Cross-session names and exact bare-name delivery in 2.1.232 are convenience
  identifiers, not authorization. Cross-session messaging, self-hosted runners,
  Remote Control, external marketplace sources, and managed sandbox overrides
  remain separately reviewed and human-gated.
- Claude Code 2.1.233 rejects Windows NT device-prefix paths that could bypass
  UNC validation and leak NTLM credentials, prevents skill/command argument
  values from being re-expanded as template markers, and fixes repeated MCP v2
  subscription reconnection against servers that terminate long-held streams
  and expands bare skill validation. These remain part of the cumulative
  baseline; they do not authorize an MCP server or skill installation.
- Version 2.1.233 also reverts the broader 2.1.232 permission changes for
  Cygwin-style symlinks and Bash input redirection while a narrower change is
  prepared. Do not treat those two checks as part of the 2.1.233 guarantee;
  retain deterministic hooks, explicit path review, least privilege, and human
  approval for affected commands.
- The opt-in `forward_user_identity` apps-gateway setting can send the signed-in
  user's identity to an upstream proxy. It remains disabled in the repository
  policy and requires a separate privacy, proxy-trust, retention, audit, and
  human-approval decision.
- Claude Code 2.1.234 extends Windows NT-namespace rejection to remaining
  pre-approval reads, session restore, includes, workflows, and uploads. It
  also redacts resolved MCP secrets, rejects marketplace allowlist host
  mismatches, preserves permission restrictions across renderer restarts, and
  clarifies repository-wide trust scope.
- Claude Code 2.1.235 fixes a permission-dialog path where Shift+Tab could
  approve an edit and grant session-wide edit permission. Permission displays
  and persistence options now match the grant, and persistent approval is
  withheld when the full contents cannot be displayed.
- Claude Code 2.1.236 makes macOS wildcard read-deny rules override allowed
  regions, cover directory contents, and survive renames. It also prevents the
  first keypress from being captured as managed-settings approval and prevents
  a Git setting from hiding untracked work from auto-mode status checks.
- Claude Code 2.1.238 requires project trust before project or added-directory
  MCP `headersHelper` execution and removes inherited credential environment
  variables from project, plugin, and agent helpers. The helper capability
  itself remains disabled until a separate command, origin, credential,
  network, and rollback review.
- Claude Code 2.1.239 prevents a request rejected by organization policy from
  being resent before the rejection is shown, preserves plan mode after cloud
  worker restarts, and corrects WebFetch cache expiry. It is the repository's
  recommended tested floor because it is the newest release with specific,
  reviewable trust-boundary evidence; the generic 2.1.240–2.1.241 release notes
  are not used to claim additional guarantees.
- This recommendation does not authorize adding credential paths, secrets,
  sandbox settings, network allowlists, runtime upgrades, or new execution
  surfaces to the repository. Inventory and approve those separately.

See `LEARNING_LEDGER.md` for dated primary-source evidence and uncertainty.

## Codex runtime notes

The repository contract remains authoritative regardless of runtime defaults.

- Codex 0.146.1 or newer is the preferred stable baseline when using models
  identified by Codex as cyber-specialized. It applies safer review defaults
  and explains permission changes in the terminal.
- Codex 0.147.0 introduced the repository's optional plugin, MCP 2026-07-28,
  and automatic-review capability records. Those remain disabled and
  human-gated.
- Codex 0.148.0 or newer is the recommended tested baseline. It prevents model
  or settings changes from leaving stale instructions or changing an active
  turn, restores persisted working directory and approval policy on resume,
  recovers MCP servers after OAuth reauthentication, and makes the sandbox fail
  closed for denied or unreadable paths across Linux and Windows.
  `codex-doctor.sh --strict-runtime` enforces that floor on a
  developer machine; normal CI validates the adapter without installing or
  upgrading Codex.
- Codex 0.148.0 can run hooks asynchronously and invoke MCP tools. That is an
  authority-expanding optional surface, not a baseline permission; the
  committed adapter does not enable it.
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
- The offline harness-evolution kernel validates sanitized aggregates and
  compares supplied candidate results. It does not ingest production telemetry,
  invoke a model, write a candidate, modify protected evals, promote, deploy,
  approve, or merge. Production signals and canaries require separate data and
  deployment contracts.
- Codex translates only reviewed read-heavy specialist roles. Claude
  write-capable agent definitions are intentionally not copied mechanically;
  parallel writes still require separate branches and worktrees.
- The Codex plugin manifest is package-ready but marketplace publication and
  installation policy remain explicit release actions.
- The Agent Plugins 1.0 core is additive and skills-only. Portable MCP
  packaging is blocked by `.agentic/mcp-compatibility.json`; client-by-client
  installation tests and removal of native compatibility files remain
  separately reviewed work.

See the [v0.1.0 release notes](../releases/v0.1.0.md) for the exact public
preview scope.
