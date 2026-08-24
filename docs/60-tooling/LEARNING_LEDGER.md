# Learning ledger

Append material, deduplicated ecosystem findings. Keep raw crawl output outside
this file.

## Entry template

### L-YYYY-MM-DD-01 — Short finding

- **State:** observed | verified | watching | proposed | trial | accepted | rejected | deferred
- **Event date:**
- **Discovered:**
- **Domains:**
- **Sources:** URLs with type and authority
- **Change:** What objectively changed
- **Repository relevance:**
- **Existing coverage:** duplicate | partial | missing
- **Scores:** relevance / authority / confidence / impact / risk / maintenance / novelty
- **Recommendation:** ignore | watch | propose | trial
- **Affected artifacts:**
- **Acceptance and verification:**
- **Uncertainty:**
- **Decision/PR:**

## Rules

- Update an existing entry instead of duplicating a recurring signal.
- Separate facts, inference, community sentiment, and recommendation.
- Record rejection/deferment so it is not rediscovered as new.
- Never store secrets, raw personal data, or untrusted executable content.

### L-2026-07-26-01 — Claude Code bounds subagents and changes nesting defaults

- **State:** proposed
- **Event date:** 2026-07-21 and 2026-07-24
- **Discovered:** 2026-07-26; corrected 2026-08-04
- **Domains:** Claude Code, orchestration, security, budget controls
- **Sources:** `https://github.com/anthropics/claude-code/releases/tag/v2.1.217`
  (first-party release, high authority);
  `https://github.com/anthropics/claude-code/releases/tag/v2.1.219`
  (first-party release, high authority);
  `https://github.com/anthropics/claude-code/blob/main/feed.xml`
  (first-party release feed, high authority)
- **Change:** Claude Code v2.1.217 added a default cap of 20 concurrently running
  subagents with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, initially disabled
  nested spawning by default, and fixed `--max-budget-usd` enforcement for
  background subagents. Version 2.1.219 then changed the default nesting depth
  to three; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` restores non-nested
  behavior. Version 2.1.219 also added `sandbox.network.strictAllowlist`.
- **Repository relevance:** The harness already requires bounded parallel work,
  explicit ownership, safety hooks, and evidence gates, but it does not name
  these runtime controls or explain how to choose conservative project limits.
- **Existing coverage:** partial
- **Scores:** relevance 5 / authority 5 / confidence 5 / impact 4 / risk 2 /
  maintenance 2 / novelty 4
- **Recommendation:** propose a documentation-only compatibility update first.
  Do not commit runtime settings until maintainers choose limits and inventory
  required network hosts.
- **Affected artifacts:** `CLAUDE.md`,
  `docs/40-execution/PARALLELIZATION.md`,
  `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/60-tooling/COMPATIBILITY.md`; optionally `.claude/settings.json` only
  after human approval
- **Acceptance and verification:** Document the two subagent environment
  controls, their current defaults, interaction with task budgets, and a
  fail-safe network-host inventory process. Preserve existing tests and run
  `./scripts/verify.sh full`. Any settings example must remain optional and
  version-qualified.
- **Uncertainty:** These defaults changed across two close releases, so runtime
  behavior must be version-qualified rather than assumed. Older Claude Code
  installations may not understand the controls. A strict
  network allowlist can break package managers, MCP servers, or documentation
  access if adopted without a project-specific host inventory.
- **Decision/PR:** Human approval required before configuring limits or network
  policy. No third-party code or new capability was enabled.

### L-2026-07-26-02 — MCP 2026-07-28 stateless revision is stable

- **State:** proposed
- **Event date:** 2026-05-29 RC; stable release 2026-07-28
- **Discovered:** 2026-07-26; stable release verified 2026-07-29
- **Domains:** MCP, transport, version negotiation, compatibility
- **Sources:** `https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28`
  (official stable specification release, highest authority);
  `https://modelcontextprotocol.io/specification/2026-07-28`
  (official specification, highest authority);
  `https://modelcontextprotocol.io/specification/2026-07-28/changelog`
  (official changelog, highest authority);
  `https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/support-2026-07-28.md`
  (official SDK migration guide, high authority)
- **Change:** The stable revision introduces a stateless core, explicit protocol-era
  negotiation, per-request client/server metadata, an extension framework, and
  revised task/subscription mechanisms. Adoption remains asynchronous across
  SDKs, clients, and servers, with version negotiation preserving compatibility
  during the transition.
- **Repository relevance:** The starter depends on project-scoped MCP servers
  and documents Perplexity, Firecrawl, and Playwright routing, but does not
  claim a protocol revision or provide a compatibility matrix.
- **Existing coverage:** partial
- **Scores:** relevance 4 / authority 5 / confidence 5 / impact 4 / risk 4 /
  maintenance 3 / novelty 5
- **Recommendation:** propose a documentation-only compatibility update and
  inventory declared support for each selected MCP server. Do not update
  `.mcp.json`, SDKs, or transport assumptions until that inventory and
  negotiation tests exist.
- **Affected artifacts:** `docs/60-tooling/MCP_STACK.md`,
  `docs/60-tooling/COMPATIBILITY.md`,
  `docs/60-tooling/SOURCES.md`, and MCP doctor expectations
- **Acceptance and verification:** Record declared protocol support for
  Perplexity, Firecrawl, and Playwright; test version negotiation without
  credentials; document fallback behavior; and preserve isolated-browser and
  human-approval controls.
- **Uncertainty:** The specification is stable, but SDK and server adoption is
  asynchronous. Selected servers may remain on the 2025 protocol for an
  undetermined period.
- **Decision/PR:** Stable status is verified. Human approval remains required
  for any dependency, server, or transport change.

### L-2026-07-28-01 — GitHub expands public-repository supply-chain safeguards

- **State:** proposed
- **Event date:** 2026-07-28
- **Discovered:** 2026-07-28; recorded 2026-07-29
- **Domains:** GitHub Actions, Dependabot, supply-chain security
- **Sources:** `https://github.blog/changelog/2026-07-28-github-actions-holds-unproven-workflows-for-approval/`
  (official GitHub changelog, high authority);
  `https://github.blog/changelog/2026-07-28-dependabot-alerts-on-malicious-packages-across-more-ecosystems/`
  (official GitHub changelog, high authority)
- **Change:** GitHub now automatically holds certain potentially malicious
  workflow runs in public repositories until a write-authorized collaborator
  approves them through an authenticated web session. Dependabot malware alerts
  now ingest OpenSSF malicious-package advisories across npm, PyPI, and other
  ecosystems.
- **Repository relevance:** The starter is public, runs pull-request workflows,
  and recommends dependency scanning. The workflow hold is automatic; expanded
  malware coverage applies only when repository malware alerts are enabled.
- **Existing coverage:** partial
- **Scores:** relevance 4 / authority 5 / confidence 5 / impact 4 / risk 1 /
  maintenance 1 / novelty 4
- **Recommendation:** document held workflow runs as a normal human approval
  state. Ask a maintainer to confirm or enable Dependabot malware alerts; do not
  automate approval of held workflows.
- **Affected artifacts:** `docs/70-collaboration/GITHUB_WORKFLOW.md`,
  `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/70-collaboration/REPOSITORY_SETUP.md`
- **Acceptance and verification:** Documentation distinguishes GitHub's
  automatic hold from a CI failure, requires inspection before approval, and
  records malware-alert enablement as a human-owned repository setting.
- **Uncertainty:** GitHub does not publish the detection criteria for held
  workflows. The automatic hold currently applies to public repositories on
  github.com, not GitHub Enterprise Server.
- **Decision/PR:** Documentation proposal only. Human approval is required to
  enable the repository setting or release a held workflow.

### L-2026-08-04-01 — Claude Code 2.1.221 adds credential masking and permission hardening

- **State:** proposed
- **Event date:** 2026-08-04
- **Discovered:** 2026-08-04
- **Domains:** Claude Code, sandboxing, credentials, permissions, plugins, Git workflow
- **Sources:** `https://github.com/anthropics/claude-code/releases/tag/v2.1.221`
  (first-party release, high authority);
  `https://code.claude.com/docs/en/sandboxing`
  (first-party security documentation, high authority)
- **Change:** Claude Code v2.1.221 added `mode: "mask"` for sandbox credential
  files on Linux and WSL, with macOS falling back to `deny`; fixed a Bash
  permission-check bypass involving hidden zsh commands inside `[[ ]]` regex
  conditionals; added plugin-validation compatibility warnings; and changed
  background sessions to preserve work, follow repository Git instructions,
  open draft PRs only when the task calls for one, and report where work lives.
- **Repository relevance:** The repository already requires scoped credentials,
  protected Git workflows, explicit draft-PR routing, and deterministic hooks,
  but it does not version-qualify the new credential masking or zsh permission
  fix. The background-session behavior confirms the existing collaboration
  contract and requires no policy change.
- **Existing coverage:** partial
- **Scores:** relevance 5 / authority 5 / confidence 5 / impact 4 / risk 2 /
  maintenance 2 / novelty 4
- **Recommendation:** document 2.1.221+ as the recommended Claude Code version
  for Linux/WSL projects that expose credential files to sandboxed commands or
  run zsh expressions through the permission analyzer. Do not add credential
  paths, masking rules, or project settings until the official settings schema
  documents the feature and a maintainer inventories the required files.
- **Affected artifacts:** `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/60-tooling/COMPATIBILITY.md`,
  `docs/40-execution/PARALLELIZATION.md`, and this ledger
- **Acceptance and verification:** Correct the prior nested-agent default,
  explain OS-specific credential behavior without example secrets, preserve
  existing Git policy, add no runtime setting, and pass repository verification.
- **Uncertainty:** The release note establishes the feature, but the public
  sandbox settings documentation does not yet provide a complete credential-file
  masking schema. macOS does not provide masking and falls back to denial.
- **Decision/PR:** Documentation-only proposal. Human approval remains required
  before configuring sandbox credential files, agent limits, or network policy.

### L-2026-08-05-01 — Claude Code 2.1.222 closes worktree and background-hook isolation gaps

- **State:** proposed
- **Event date:** 2026-08-04
- **Discovered:** 2026-08-05
- **Domains:** Claude Code, worktrees, hooks, background agents, permissions, remote control
- **Sources:** `https://github.com/anthropics/claude-code/releases/tag/v2.1.222`
  (first-party release, high authority)
- **Change:** Claude Code v2.1.222 fixed worktree-isolated sessions and their
  subagents being able to run destructive Git commands against the main
  checkout; fixed `PreToolUse` auto-allow hooks bypassing tool restrictions in
  background agent tasks; added permission classification to cross-session
  `SendMessage`; and prevented repository-local settings from turning on Remote
  Control. Repository-local settings may still turn Remote Control off.
- **Repository relevance:** The harness explicitly uses worktrees, subagents,
  background work, deterministic hooks, and repository-local Claude settings.
  Those are direct matches for the corrected boundaries.
- **Existing coverage:** partial
- **Scores:** relevance 5 / authority 5 / confidence 5 / impact 5 / risk 1 /
  maintenance 1 / novelty 5
- **Recommendation:** recommend Claude Code 2.1.222+ whenever worktree isolation,
  background agent tasks, or auto-allow hooks are relied upon. Retain
  destructive-command hooks, scoped permissions, and human approval because a
  runtime fix is not a substitute for layered controls. Do not silently pin or
  upgrade the runtime.
- **Affected artifacts:** `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/60-tooling/COMPATIBILITY.md`, and this ledger
- **Acceptance and verification:** Record the affected boundaries and minimum
  recommended version without adding settings, credentials, dependencies, or
  capabilities; preserve current worktree and hook policy; pass full repository
  verification.
- **Uncertainty:** The release notes establish the fixed behaviors but do not
  publish a CVE, exploit prerequisites, or affected-version floor. Treat
  versions before 2.1.222 as lacking these fixes without inferring a remotely
  exploitable vulnerability.
- **Decision/PR:** Documentation-only proposal. Human approval remains required
  for runtime upgrades, permission changes, Remote Control, or hook changes.

### L-2026-08-05-02 — Codex 0.146.1 adds safer cyber-model review defaults

- **State:** proposed
- **Event date:** 2026-08-05
- **Discovered:** 2026-08-05
- **Domains:** Codex, model selection, automatic review, permissions, cyber safety
- **Sources:** `https://github.com/openai/codex/releases/tag/rust-v0.146.1`
  (first-party stable release, high authority);
  `https://github.com/openai/codex/pull/37057`
  (first-party implementation and tests, high authority)
- **Change:** Codex 0.146.1 applies safer automatic-review defaults for models
  identified as cyber-specialized and explains permission changes in the
  terminal. The implementation respects managed permission requirements,
  prefers automatic review when allowed, otherwise falls back to user approval,
  and warns before broader access.
- **Repository relevance:** The harness supports Codex by contract and requires
  scoped permissions, explicit approval, and separate evaluation. The new
  runtime default reinforces those rules but must not be mistaken for project
  authorization or a replacement for repository gates.
- **Existing coverage:** partial
- **Scores:** relevance 4 / authority 5 / confidence 5 / impact 4 / risk 1 /
  maintenance 1 / novelty 4
- **Recommendation:** document Codex 0.146.1+ as the preferred stable baseline
  when cyber-specialized models are available. Preserve project permission
  profiles, human approval, and security review; do not enable a model,
  automatic reviewer, or broader access automatically.
- **Affected artifacts:** `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/60-tooling/COMPATIBILITY.md`, and this ledger
- **Acceptance and verification:** Describe the safer default narrowly, keep
  repository policy authoritative, add no model or permission configuration,
  and pass full repository verification.
- **Uncertainty:** The behavior is limited to models whose catalog metadata
  identifies them as cyber-specialized and to clients that consume the new
  defaults. It does not guarantee that every Codex surface or older session
  adopts the same reviewer state.
- **Decision/PR:** Documentation-only proposal. Human approval remains required
  for model selection, permission profiles, automatic review, and external
  actions.

### L-2026-08-06-01 — Claude Code 2.1.223 closes shell and workflow policy gaps

- **State:** proposed
- **Event date:** 2026-08-06
- **Discovered:** 2026-08-06
- **Domains:** Claude Code, shell permissions, approval prompts, workflow sandboxing, managed policy
- **Sources:** `https://github.com/anthropics/claude-code/releases/tag/v2.1.223`
  (first-party release, high authority)
- **Change:** Claude Code v2.1.223 fixed a Bash permission bypass that could
  conceal part of a crafted command; prevented tabs and invisible Unicode from
  hiding command content in approval prompts; blocked workflow-script dynamic
  imports from escaping the workflow sandbox; and made an organization's
  bypass-permissions disable policy apply to agent definitions that request
  `bypassPermissions` mode.
- **Repository relevance:** The harness runs shell tools, treats approval text
  as review evidence, supports workflow agents, and requires managed policy and
  least privilege to remain authoritative. These fixes directly strengthen
  those trust boundaries.
- **Existing coverage:** partial
- **Scores:** relevance 5 / authority 5 / confidence 5 / impact 5 / risk 1 /
  maintenance 1 / novelty 5
- **Recommendation:** recommend Claude Code 2.1.223+ whenever shell permission
  analysis, workflow-agent sandboxing, or managed bypass-permission policy is
  relied upon. Keep deterministic hooks, scoped permissions, workflow review,
  and human approval because the runtime fixes do not replace layered controls.
  Do not silently pin or upgrade the runtime.
- **Affected artifacts:** `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/60-tooling/COMPATIBILITY.md`, `CHANGELOG.md`, and this ledger
- **Acceptance and verification:** Record the affected boundaries and minimum
  recommended version; add no runtime, agent-mode, permission, workflow, or
  managed-setting configuration; preserve existing security gates; pass full
  repository verification.
- **Uncertainty:** The release note does not publish a CVE, exploit
  prerequisites, or affected-version floor. Treat versions before 2.1.223 as
  lacking these fixes without inferring remote exploitability or guaranteed
  exposure in every configuration.
- **Decision/PR:** Documentation-only proposal. Human approval remains required
  for runtime upgrades, agent modes, permission policy, workflow changes, or
  managed settings.

### L-2026-08-12-01 — Agent Plugins 1.0 establishes a portable skills and MCP package format

- **State:** trial
- **Event date:** 2026-08-06; GitHub availability announced 2026-08-12
- **Discovered:** 2026-08-13
- **Domains:** Agent Plugins, Agent Skills, MCP, Codex, portability, enterprise governance
- **Sources:** `https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md`
  (canonical specification, highest authority);
  `https://github.com/agentplugins/agent-plugins-example`
  (canonical example and migration guide, high authority);
  `https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app/`
  (first-party GitHub availability announcement, high authority)
- **Change:** Agent Plugins 1.0 defines a required closed root `plugin.json`,
  fixed `skills/` discovery, optional root `mcp.json`, path containment, and
  reverse-domain client extensions. The core has no portable hooks, commands,
  arbitrary interface fields, OAuth configuration, or secret-reference field.
- **Repository relevance:** The repository already exposed skills through a
  root link but placed Codex-specific package metadata under `.codex-plugin/`
  and used fields that are invalid in the portable closed manifest. Its
  project `.mcp.json` also depends on client-specific environment expansion.
- **Existing coverage:** partial
- **Scores:** relevance 5 / authority 5 / confidence 5 / impact 4 / risk 2 /
  maintenance 2 / novelty 5
- **Recommendation:** add the portable manifest and offline containment checks
  additively, retain the working Codex-native surface, and defer portable MCP
  entries until a separate server/client credential and protocol review.
- **Affected artifacts:** root `plugin.json`, `skills/`, Codex packaging docs,
  compatibility/security docs, plugin doctor, tests, and durable state
- **Acceptance and verification:** Closed manifest; no inline components;
  contained immediate-child skill discovery; native manifest remains valid;
  project `.mcp.json` is not presented as portable; targeted and full
  repository verification pass.
- **Uncertainty:** Portable package conformance does not prove that every
  client implements identical installation, trust, MCP, or extension behavior.
  Codex-native compatibility is retained until client-specific tests justify
  removal.
- **Decision/PR:** T-034 is an additive implementation trial. Publishing,
  installation, portable MCP execution, credentials, authority changes,
  approval, and merge remain human-controlled and out of scope.

### L-2026-08-14-01 — Claude Code 2.1.232 changes subagent defaults and closes cumulative runtime boundary gaps

- **State:** trial
- **Event dates:** 2026-08-11 through 2026-08-13
- **Discovered:** 2026-08-14
- **Domains:** Claude Code, subagents, context inheritance, background work,
  skills, shell permissions, sandboxing, repository trust, cross-session messaging, MCP
- **Sources:** `https://github.com/anthropics/claude-code/releases/tag/v2.1.228`,
  `https://github.com/anthropics/claude-code/releases/tag/v2.1.229`,
  `https://github.com/anthropics/claude-code/releases/tag/v2.1.231`, and
  `https://github.com/anthropics/claude-code/releases/tag/v2.1.232`
  (first-party releases, high authority)
- **Change:** v2.1.228 hardens synced skills against local command/MCP
  shadowing and local body execution. v2.1.229 hardens IPv6 sandbox parsing
  and dangerous Git flags while adding optional self-hosted hooks and dynamic
  marketplace command sources. v2.1.231 fixes pre-registered MCP OAuth redirect
  handling. v2.1.232 makes forked subagents inherit the full conversation and
  prompt cache by default, backgrounds non-teammate interactive spawns, and
  fixes PowerShell, Git Bash symlink, nested-repository trust, Bash redirection,
  shared-socket, Linux sandbox, and sandbox-binary override boundaries.
- **Repository relevance:** The harness uses skills, shell commands,
  worktrees, read-only specialists, background delegation, MCP clients, and
  cross-runtime policy. The new defaults directly affect context minimization,
  ownership, completion evidence, and compatibility guidance.
- **Existing coverage:** partial; prior entries covered 2.1.221–2.1.225. This
  entry is deduplicated to material changes in 2.1.228–2.1.232 and does not
  repeat unrelated UI or provider fixes.
- **Scores:** relevance 5 / authority 5 / confidence 5 / impact 5 / risk 1 /
  maintenance 1 / novelty 5
- **Recommendation:** raise the read-only advisory and tested Claude Code floor
  to 2.1.232. Preserve the project contract: fork only necessary context, keep
  in-session specialists read-only, isolate writers, await evidence, and keep
  self-hosted, cross-session, Remote Control, marketplace command, MCP, and
  sandbox-setting authority separately human-gated.
- **Affected artifacts:** `.agentic/runtime-baselines.json`, `CLAUDE.md`,
  `AGENTS.md`, `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/60-tooling/COMPATIBILITY.md`, runtime tests, and durable state
- **Acceptance and verification:** strict simulation rejects 2.1.231 and
  accepts 2.1.232; advisory and JSON output remain read-only; optional
  capability gates remain false and human-controlled; full repository
  verification passes.
- **Uncertainty:** The release notes do not publish CVEs, complete exploit
  prerequisites, or a full affected-version floor. A fixed behavior therefore
  proves only that earlier versions lack the documented fix, not that every
  earlier installation is exploitable. Runtime availability also does not prove
  configuration or authorization.
- **Decision/PR:** T-036 is a bounded compatibility-policy trial. It does not
  install or upgrade a runtime, enable a capability, change settings, expand
  credentials/network/sandbox authority, deploy, approve, or merge. Human
  approval remains required before finalization and landing.

### L-2026-08-16-01 — Claude Code 2.1.233 closes Windows path and skill-argument boundaries

- **State:** trial
- **Event date:** 2026-08-14
- **Discovered:** 2026-08-16
- **Domains:** Claude Code, Windows, credentials, skills, MCP, runtime compatibility
- **Source:** `https://github.com/anthropics/claude-code/releases/tag/v2.1.233`
  (first-party release, high authority)
- **Change:** v2.1.233 rejects Windows NT device-prefix paths that could bypass
  UNC validation and leak NTLM credentials, and prevents skill/command argument
  values from being re-expanded as template markers. It also fixes repeated MCP
  v2 subscription reconnection against servers that terminate long-held streams
  and validates bare skill directories more completely. The same release adds
  opt-in apps-gateway user-identity forwarding and reverts the broader 2.1.232
  permission changes for Cygwin-style symlinks and Bash input redirection.
- **Repository relevance:** The starter supports native runtime adapters,
  external and project-local skills, Windows on a best-effort basis, and
  project-scoped MCP clients. The path and argument fixes strengthen existing
  trust boundaries; the MCP fix improves reliability without changing the
  repository's blocked portable-MCP decision.
- **Existing coverage / duplicate status:** new relative to the 2.1.232 entry.
  Unrelated UI, gateway, provider, and self-hosted performance changes are
  intentionally omitted.
- **Scores:** relevance 5 / authority 5 / confidence 5 / impact 4 / risk 1 /
  maintenance 1 / novelty 4
- **Recommendation:** raise the read-only advisory and tested Claude Code floor
  to 2.1.233. Record the Windows path, literal argument, and MCP v2 reliability
  behaviors without installing a runtime, enabling an MCP server, or expanding
  credential, network, sandbox, plugin, approval, or production authority.
  Record the two reverted permission changes as exclusions and keep identity
  forwarding disabled pending a separate privacy and proxy-trust review.
- **Affected artifacts:** `.agentic/runtime-baselines.json`,
  `docs/30-engineering/SECURITY_MODEL.md`,
  `docs/60-tooling/COMPATIBILITY.md`, runtime tests, and durable state
- **Acceptance and verification:** strict simulation rejects 2.1.232 and
  accepts 2.1.233; advisory and JSON output remain read-only; optional
  capability gates remain false and human-controlled; tests preserve the
  input-redirection regression warning; full repository verification passes.
- **Uncertainty:** The release notes do not publish a CVE, exploit prerequisites,
  or a complete affected-version range for the NTLM vector. The MCP note proves
  a documented client reliability fix, not compatibility with every server or
  authorization to connect one.
- **Decision/PR:** T-038 is a bounded compatibility-policy trial. Issue #55
  owns human review. Installation, configuration, capability activation,
  credentials, network/sandbox authority, approval, deployment, production,
  and merge remain out of scope.

### L-2026-08-23-01 — Self-evolving systems need an evidence-gated harness loop

- **State:** trial
- **Event date:** 2026-08-18
- **Discovered:** 2026-08-23
- **Domains:** harness engineering, evaluation, continual improvement, safety,
  cost, latency, enterprise governance
- **Sources:**
  - `https://spandyie.github.io/blog/2026/08/18/how-to-build-self-evolving-enterprise-agents/`
    (independent synthesis, medium authority)
  - `https://arxiv.org/abs/2508.07407` (research survey, primary source)
  - `https://arxiv.org/abs/2509.26354` (Misevolution research, primary source)
  - `https://arxiv.org/abs/2601.18734` (OPSD research, primary source)
- **Change:** The sources distinguish outcome-driven improvement of prompts,
  examples, memory, and orchestration from model-weight training. The recurring
  safe loop is act, collect bounded signals, evaluate a candidate against an
  incumbent, gate regressions and operational budgets, and promote only under
  explicit governance.
- **Repository relevance:** The repository already researches external changes
  and records durable state, but it did not have a deterministic way to compare
  a bounded harness candidate with the last-known-good behavior.
- **Existing coverage:** partial. The ecosystem research loop, task ledger,
  evaluator separation, security gates, and human merge boundary existed;
  sanitized outcome schemas, protected regression cases, integrity digests,
  and incumbent-versus-candidate gates were missing.
- **Scores:** relevance 5 / authority 4 / confidence 4 / impact 5 / risk 5 /
  maintenance 3 / novelty 4
- **Recommendation:** trial an offline, proposal-only kernel. Begin with
  examples, instructions, memory curation, and routing. Do not add production
  telemetry, raw trace retention, generated-code execution, model training,
  automatic eval mutation, canaries, or autonomous promotion.
- **Affected artifacts:** `.agentic/evolution/`, `scripts/evolution_engine.py`,
  `docs/30-engineering/HARNESS_EVOLUTION.md`, evaluation guidance, security
  model, routing skill, tests, and durable state
- **Acceptance and verification:** closed policy and schemas; sanitized signal
  rejection tests; immutable policy/eval fingerprints; exact protected-case
  coverage; quality, regression, safety, cost, and latency gates; proposal-only
  result; deterministic offline and generated-project verification.
- **Uncertainty:** The independent article is a useful synthesis, not a
  production safety standard. The linked research demonstrates approaches in
  bounded settings and does not establish that autonomous online learning is
  safe for this starter. Domain calibration, privacy, statistical confidence,
  canaries, and rollback remain future, separately reviewed work.
- **Decision/PR:** T-041 implements only the offline comparison contract. Issue
  #60 owns human review. It does not collect production data, invoke remote
  models, train weights, write candidates, change protected evals, promote,
  deploy, approve, or merge.
