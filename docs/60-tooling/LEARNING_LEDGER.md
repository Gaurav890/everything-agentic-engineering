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

### L-2026-07-26-01 — Claude Code adds bounded subagent and stricter sandbox controls

- **State:** proposed
- **Event date:** 2026-07-24
- **Discovered:** 2026-07-26
- **Domains:** Claude Code, orchestration, security, budget controls
- **Sources:** `https://github.com/anthropics/claude-code/releases/tag/v2.1.219`
  (first-party release, high authority);
  `https://github.com/anthropics/claude-code/blob/main/feed.xml`
  (first-party release feed, high authority)
- **Change:** Claude Code v2.1.219 added a default cap of 20 concurrently running
  subagents with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, disabled nested
  subagent spawning by default unless
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` is set, fixed
  `--max-budget-usd` enforcement for background subagents, and added
  `sandbox.network.strictAllowlist`.
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
- **Uncertainty:** The release note establishes behavior in v2.1.219, but older
  Claude Code installations may not understand the new settings. A strict
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
