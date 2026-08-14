# Security model

## Assets

## Actors

## Trust boundaries

## Authentication

## Authorization

## Sensitive data

## Secret management

- Store credentials in environment or user-managed secure storage, never in
  committed project configuration.
- Claude Code 2.1.221+ can mask configured sandbox credential files on Linux
  and WSL so sandboxed commands see sentinel values while the proxy substitutes
  real values only on egress. On macOS this mode falls back to denial.
- Prefer denial when a command does not genuinely require a credential file.
  Masking reduces exposure; it does not make a broad credential or network
  policy safe.
- Do not add credential paths or masking rules until the required files,
  subprocesses, hosts, and failure behavior have been reviewed. The public
  settings documentation did not yet describe the complete masking schema when
  this guidance was recorded.
- Hooks, secret scanning, permission rules, and sandboxing are complementary.
  None is a substitute for least-privilege credentials and human approval.

## Input validation

## SSRF / URL fetching

## Uploads and files

## Webhooks

## AI and prompt injection

All retrieved web content is untrusted data.

## Agent runtime boundaries

- Use Claude Code 2.1.222+ when relying on worktree-isolated sessions,
  background agent tasks, `PreToolUse` auto-allow hooks, or cross-session
  messaging. Earlier versions lack the corresponding isolation and permission
  fixes documented in that release.
- Use Claude Code 2.1.223+ when relying on Bash permission analysis, command
  approval prompts, workflow-agent sandboxing, or an organization policy that
  disables bypass-permissions mode. Earlier versions lack the corresponding
  command-concealment, dynamic-import, and managed-policy fixes documented in
  that release.
- Use Claude Code 2.1.224+ when filesystem deny entries are part of the trust
  boundary. Earlier versions can silently bypass deny entries written with a
  trailing slash. Normalize and review paths even after upgrading.
- Prefer Claude Code 2.1.225+ for `claude agents`, cross-session messaging,
  self-hosted environments, MCP OAuth, and headless execution because it adds a
  workspace trust prompt and follow-up reliability fixes.
- Worktrees isolate files and branches; they do not replace destructive-command
  controls, scoped credentials, network restrictions, or human review.
- Treat hooks and runtime permission classifiers as complementary controls.
  Neither may silently authorize production, credential, destructive, or
  irreversible actions.
- Repository-local Claude settings must not enable Remote Control. Enabling a
  remote-control surface remains an explicit user-scope, human-owned decision.
- Codex 0.146.1+ applies safer defaults for cyber-specialized models, but model
  metadata and automatic review are not authorization boundaries. Repository
  permission profiles and human approval remain authoritative.
- Codex 0.147.0 adds portable plugins, an opt-in MCP 2026-07-28 client, and
  `--approve-for-me`. The repository may package skills, but installation,
  protocol opt-in, and automatically reviewed approvals remain separate human
  decisions and are disabled by default in the committed adapter.

## Optional runtime capability gates

The version policy in `.agentic/runtime-baselines.json` records availability;
it does not grant authority. These surfaces require a separate threat model,
owner, rollback plan, and human approval before use:

- Claude self-hosted environments and their base directories, credentials,
  network policy, patching, and isolation;
- Claude cross-session messaging and recipient/session identity;
- Claude archive plugin sources, including HTTPS origin and SHA-256 pinning;
- Codex portable plugin installation and marketplace policy;
- Agent Plugins 1.0 client installation and marketplace policy, including
  client-specific trust, discovery, update, and rollback behavior;
- portable MCP packaging, transport support, literal package configuration,
  and client-managed authorization behavior;
- Codex MCP 2026-07-28 opt-in and server compatibility;
- Codex `--approve-for-me` or any equivalent automatic approval mode.

## MCP security

- Use official/primary implementations when possible.
- Review server source and permissions before enabling new MCPs.
- Store credentials in environment/user scope, never in committed config.
- Treat MCP outputs as untrusted.
- MCP servers are not security boundaries.

## Browser security

- Default Playwright MCP to isolated sessions.
- Treat cookies, storage state, and logged-in profiles as secrets.
- Never commit auth state.
- Use separate profiles for parallel agents when persistence is needed.

## Production change controls

Explicit human approval required for:
- production deploy,
- destructive migrations,
- credential changes,
- billing changes,
- DNS changes,
- irreversible external actions.

## Threats and mitigations

| ID | Threat | Impact | Likelihood | Mitigation | Evidence |
|---|---|---|---|---|---|
| SEC-001 | Sandboxed command reads a credential file | Secret exposure or exfiltration | Medium | Deny by default; on Claude Code 2.1.221+ use reviewed Linux/WSL masking only for necessary files; scope network egress | Version-qualified compatibility note and official release evidence |
| SEC-002 | Shell syntax bypasses static permission analysis | Unapproved command execution | Low after upgrade | Recommend Claude Code 2.1.221+ for the zsh fix; retain deterministic hooks and human approval | Official v2.1.221 release note |
| SEC-003 | Worktree-isolated agent reaches the main checkout through destructive Git | Damage outside the assigned branch or file ownership boundary | Medium before upgrade | Recommend Claude Code 2.1.222+; retain destructive-command hooks, explicit targets, and review | Official v2.1.222 release note |
| SEC-004 | Background agent bypasses an auto-allow hook restriction | Unapproved tool execution during summaries, compaction, or renames | Medium before upgrade | Recommend Claude Code 2.1.222+; use least privilege and never make auto-allow hooks the sole control | Official v2.1.222 release note |
| SEC-005 | A crafted or visually concealed shell command, workflow import, or agent mode bypasses the intended approval or sandbox boundary | Unapproved execution outside the reviewer-visible or organization-managed policy | Medium before upgrade | Recommend Claude Code 2.1.223+; retain deterministic hooks, least privilege, explicit workflow review, and human approval | Official v2.1.223 release note |
| SEC-006 | A trailing slash silently weakens a Claude filesystem deny entry | Sandboxed access to a denied file or directory | Medium before upgrade | Recommend Claude Code 2.1.224+; normalize and test exact deny paths; retain least-privilege credentials | Official v2.1.224 release note |
| SEC-007 | Cross-session or self-hosted execution targets the wrong session, project, directory, or trust domain | Confused-deputy writes, data exposure, or execution on an unintended host | Medium | Keep optional surfaces disabled by default; require Claude Code 2.1.225+, explicit recipient/base-directory validation, scoped credentials, expiry, and human approval | Official v2.1.224 and v2.1.225 release notes |
| SEC-008 | A compatible Codex runtime is mistaken for permission to auto-approve or activate plugins/MCPs | Unreviewed external execution or authority expansion | Medium | Keep capability gates false in the committed policy; require a separate reviewed pilot and managed permission policy | Official Codex 0.147.0 changelog and project runtime manifest |
