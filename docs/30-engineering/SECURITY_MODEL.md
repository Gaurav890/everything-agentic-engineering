# Security model

## Assets

## Actors

## Trust boundaries

## Authentication

The enterprise reference UI uses an explicit local actor selector for
demonstration only. It is not authentication. Production must derive actor,
role, and tenant claims from a reviewed identity provider on the server.

## Authorization

The service and pure domain policy deny unknown roles, cross-tenant access,
requester access outside ownership, reviewer access outside eligibility,
self-approval, invalid state transitions, incomplete evidence, failed policy
gates, and missing decision rationale. Creation and evidence-check audit events
are constructed inside the trusted service boundary from the verified actor or
local policy engine; callers cannot supply attribution or transition metadata.
Production must enforce the same policy server-side before mutation and again
inside tenant-scoped persistence boundaries.

## Sensitive data

The committed enterprise fixture is synthetic. Production request scope,
justification, evidence, identity, and rationale require classification,
least-privilege access, encryption, retention, audit, and safe logging policy.

## Secret management

- Store credentials in environment or user-managed secure storage, never in
  committed project configuration.
- Claude Code 2.1.221+ can mask configured sandbox credential files on Linux
  and WSL so sandboxed commands see sentinel values while the proxy substitutes
  real values only on egress. On macOS this mode falls back to denial.
- Claude Code 2.1.232 adds redaction for additional GitLab token families and
  protects the `glab` CLI credential store like the `gh` store. This is defense
  in depth; GitLab credentials still belong in user-managed secure storage and
  outside committed project configuration.
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
- Use Claude Code 2.1.228+ when synced skills are part of the trust boundary;
  earlier versions lack the documented command/MCP shadowing, description, and
  local body-execution hardening. Continue to review synced and third-party
  skills as untrusted data.
- Prefer Claude Code 2.1.232+ for `claude agents`, nested repository trust,
  PowerShell permission analysis, Linux sandbox path enforcement,
  cross-session messaging, self-hosted environments, MCP OAuth, and headless
  execution because it includes the documented hardening through that release.
- Claude Code 2.1.232 forked subagents inherit the full conversation and prompt
  cache, while non-teammate interactive spawns run in the background. Limit
  inherited context, keep in-session specialists read-only, isolate writers in
  branches/worktrees, and await evidence. A background worker is not a new
  trust domain and does not gain approval or merge authority.
- Prefer Claude Code 2.1.233+ on native Windows or when skill arguments can
  contain user-controlled template-like text. Earlier versions lack the
  documented NT device-prefix validation and argument re-expansion fixes.
  Continue to treat skill arguments as untrusted input and keep credentials
  outside repository state.
- Claude Code 2.1.233 reverts the broader 2.1.232 Cygwin-symlink and Bash
  input-redirection permission changes. Do not rely on those checks at this
  baseline; retain deterministic hooks, explicit path review, least privilege,
  and human approval.
- Keep the 2.1.233 opt-in apps-gateway `forward_user_identity` setting disabled
  until the upstream proxy, transmitted identity fields, retention, audit,
  access controls, and user/administrator expectations receive a separate
  privacy and authorization review.
- Prefer Claude Code 2.1.239+ for the cumulative runtime-security fixes added
  in 2.1.234–2.1.239. Those releases harden remaining Windows pre-approval
  paths and marketplace origins, prevent permission-dialog grants from
  exceeding the visible request, make macOS wildcard denies survive directory
  renames, require trust before project MCP `headersHelper` execution, isolate
  helper processes from inherited credential environment variables, and avoid
  replaying organization-policy rejections.
- Keep marketplace and MCP `headersHelper` commands disabled until their
  executable origin, arguments, output contract, credential environment,
  update path, failure behavior, and rollback have separate human review.
  A trusted project does not automatically make a helper trustworthy.
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
- Prefer Codex 0.148.0+ because it prevents stale instructions after runtime
  configuration changes, restores the working directory and approval policy
  when a session resumes, recovers MCP after OAuth reauthentication, and fails
  closed for denied or unreadable filesystem paths on Linux and Windows.
- Codex 0.148.0 also makes asynchronous hooks and hooks that invoke MCP tools
  available. They remain disabled until hook provenance, ordering, failure
  semantics, MCP authority, credentials, network access, auditability, and
  rollback receive a separate human-reviewed threat model.

## Optional runtime capability gates

The version policy in `.agentic/runtime-baselines.json` records availability;
it does not grant authority. These surfaces require a separate threat model,
owner, rollback plan, and human approval before use:

- Claude self-hosted environments and their base directories, credentials,
  network policy, patching, and isolation;
- Claude cross-session messaging and recipient/session identity;
- Claude archive plugin sources, including HTTPS origin and SHA-256 pinning;
- Claude apps-gateway user-identity forwarding and its proxy/privacy contract;
- Claude marketplace and MCP `headersHelper` commands, executable provenance,
  credential isolation, and rollback behavior;
- Codex portable plugin installation and marketplace policy;
- Agent Plugins 1.0 client installation and marketplace policy, including
  client-specific trust, discovery, update, and rollback behavior;
- portable MCP packaging, transport support, literal package configuration,
  and client-managed authorization behavior;
- Codex MCP 2026-07-28 opt-in and server compatibility;
- Codex asynchronous hooks and hooks that invoke MCP tools;
- Codex `--approve-for-me` or any equivalent automatic approval mode.

## Harness evolution security

Harness evolution is an offline evaluation and proposal surface, not an
authority-expanding runtime. Its committed policy, schemas, protected cases,
incumbent evidence, and comparator are part of the trust boundary.

- Accept only sanitized aggregate outcome signals. Reject raw prompts,
  outputs, source code, secrets, credentials, personal data, email addresses,
  and user identifiers rather than attempting best-effort redaction.
- Fingerprint the policy and protected eval set. Incumbent and candidate
  evidence must reference the exact same immutable exam.
- Keep candidate-owned paths separate from policy, eval, security, workflow,
  dependency, credential, and comparator paths.
- Require complete case coverage, a distinct builder and evaluator, zero
  protected regressions, zero safety failures, and bounded cost and latency.
- Treat a passing comparison as permission to open a human-reviewed proposal
  only. It never authorizes writing a candidate, changing an eval, promotion,
  deployment, approval, merge, or production access.
- Synthetic starter evidence demonstrates the contract, not product quality.
  Downstream teams must provide domain-owned, privacy-reviewed evals before
  relying on the result.

## MCP security

- Use official/primary implementations when possible.
- Review server source and permissions before enabling new MCPs.
- Store credentials in environment/user scope, never in committed config.
- Treat MCP outputs as untrusted.
- MCP servers are not security boundaries.
- Project MCP configuration and portable plugin packaging are different trust
  decisions. Never copy `.mcp.json` into root `mcp.json` mechanically.
- Treat `npx` server commands as external package execution. A version observed
  during review is not an immutable execution pin, and `@latest` is mutable.
- Portable MCP packaging remains blocked by
  `.agentic/mcp-compatibility.json` until portable credentials, deterministic
  resolution, protocol negotiation, client trust/rollback, and security review
  all have evidence.

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
| SEC-009 | Project MCP configuration is copied into a portable plugin despite missing portable credential and execution contracts | Secret mishandling, mutable package execution, or silent network/browser authority | High | Keep root `mcp.json` absent; validate `.agentic/mcp-compatibility.json`; require all portable gates and a separate human-approved PR | T-035 compatibility matrix, negative tests, and security evidence |
| SEC-010 | A forked or background subagent receives broader context or write authority than its bounded task requires | Secret exposure, conflicting edits, or unreviewed integration | Medium | Use Claude Code 2.1.232+; fork only necessary context; keep in-session specialists read-only; isolate writers; await and independently evaluate results | Official v2.1.232 release note and repository agent contract |
| SEC-011 | PowerShell, nested-repository trust, shared-socket, or Linux sandbox-path behavior bypasses the intended permission boundary | Unapproved file access, writes, session targeting, or binary substitution | Medium before upgrade | Recommend Claude Code 2.1.232+ for the documented fixes; retain deterministic hooks, explicit paths, least privilege, and managed approval | Official v2.1.232 release note |
| SEC-012 | A synced skill shadows a local command/MCP prompt or executes hidden local directives/imports | Instruction substitution or unreviewed local execution | Medium before upgrade | Require Claude Code 2.1.228+; treat synced skills as untrusted; preserve project-local skill authority and review | Official v2.1.228 release note |
| SEC-013 | A Windows NT device-prefix path bypasses UNC validation and triggers credential-bearing network access | NTLM credential disclosure to an unintended network target | Medium on affected native Windows workflows before upgrade | Require Claude Code 2.1.233+ on native Windows; retain explicit path validation, least-privilege credentials, and network controls | Official v2.1.233 release note |
| SEC-014 | A skill or command argument is re-expanded as a template marker after substitution | Instruction or data substitution outside the caller's intended literal argument | Medium before upgrade | Require Claude Code 2.1.233+; validate arguments at trust boundaries and treat external skill inputs as untrusted data | Official v2.1.233 release note |
| SEC-015 | A maintainer assumes 2.1.233 still enforces the reverted Cygwin-symlink or Bash input-redirection permission changes | Commands receive less runtime permission scrutiny than policy assumes | Medium | Do not claim those checks at 2.1.233; retain deterministic hooks, explicit path review, least privilege, and human approval | Official v2.1.233 release note |
| SEC-016 | Apps-gateway identity forwarding exposes signed-in user identity to an insufficiently governed proxy | Privacy leakage, unexpected attribution, or identity retention outside the intended boundary | Medium if enabled | Keep forwarding disabled; require proxy, field, retention, access, audit, disclosure, and rollback review before enablement | Official v2.1.233 release note and runtime manifest gate |
| SEC-017 | Raw traces, prompts, outputs, source, secrets, or identifiers enter an evolution dataset | Privacy breach, credential exposure, or durable retention of sensitive material | High if collection is added carelessly | Accept only closed aggregate signals; reject forbidden fields; require a separate data architecture before production collection | Evolution signal schema and negative tests |
| SEC-018 | A candidate improves its score by changing the policy, cases, evaluator, or comparator | Evaluation gaming and unsafe promotion | Medium | Pin policy and eval SHA-256 digests; protect exam and control paths; require builder/evaluator separation and exact case coverage | Evolution policy, protected eval set, and comparator tests |
| SEC-019 | A noisy or incomplete candidate appears better than the incumbent | Regression, increased cost, or degraded latency | Medium | Fail closed on missing cases; require weighted gain, zero protected regressions and safety failures, plus cost and p95 latency budgets | Deterministic incumbent-versus-candidate gate tests |
| SEC-020 | A passing offline comparison is mistaken for approval to deploy or modify the harness | Unreviewed authority expansion or production change | Medium | Hard-code proposal-only authority; report promotion as unauthorized; preserve issue, PR, code-owner, human approval, and merge gates | Evolution policy, CLI output, and repository workflow |
| SEC-021 | A remaining Windows pre-approval path, marketplace host mismatch, or MCP diagnostic leaks credentials or reaches an unintended origin | Credential disclosure or unreviewed external execution | Medium before upgrade | Require Claude Code 2.1.234+; keep marketplace origins allowlisted, resolved secrets out of diagnostics, and credentials least-privileged | Official v2.1.234 release note |
| SEC-022 | A permission dialog grants broader or longer-lived authority than the reviewer can see | Accidental session-wide write permission or concealed command/path approval | Medium before upgrade | Require Claude Code 2.1.235+; preserve visible-request fidelity, deterministic hooks, and human review | Official v2.1.235 release note |
| SEC-023 | A macOS wildcard deny is bypassed through a directory rename, a managed prompt consumes an unintended keypress, or hidden untracked files make a worktree look clean | Denied file access, accidental managed approval, or unsafe Git automation | Medium before upgrade | Require Claude Code 2.1.236+; keep deny tests, explicit approval, and independent Git-state checks | Official v2.1.236 release note |
| SEC-024 | A project or plugin MCP helper executes before trust or inherits credential-bearing environment variables | Untrusted code execution or credential exposure | Medium before upgrade; high if helper enabled without review | Require Claude Code 2.1.238+; keep helpers disabled by default; require provenance, environment, arguments, output, failure, and rollback review | Official v2.1.238 release note and runtime manifest gate |
| SEC-025 | A request rejected by organization policy is replayed, or a resumed cloud session loses plan mode | Duplicate external effects or execution outside the intended review phase | Medium before upgrade | Require Claude Code 2.1.239+; retain idempotency, policy logging, and explicit resumed-state review | Official v2.1.239 release note |
| SEC-026 | Codex retains stale instructions, resumes with the wrong approval policy or working directory, fails open on unreadable paths, or silently loses MCP after reauthentication | Incorrect execution context, permission drift, file exposure, or degraded control visibility | Medium before upgrade | Require Codex 0.148.0+; keep filesystem denials fail-closed and validate resumed state; leave async/MCP-invoking hooks disabled pending separate review | Official Codex 0.148.0 release note and runtime manifest gates |
