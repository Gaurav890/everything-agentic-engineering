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
