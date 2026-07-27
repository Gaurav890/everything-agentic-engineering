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

### L-2026-07-26-02 — MCP 2026-07-28 stateless revision remains a release candidate

- **State:** watching
- **Event date:** 2026-05-29 RC; final release scheduled for 2026-07-28
- **Discovered:** 2026-07-26
- **Domains:** MCP, transport, version negotiation, compatibility
- **Sources:** `https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28-RC`
  (official specification release, highest authority);
  `https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/`
  (official release announcement, high authority);
  `https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/support-2026-07-28.md`
  (official SDK migration guide, high authority)
- **Change:** The RC introduces a stateless core, explicit protocol-era
  negotiation, per-request client/server metadata, an extension framework, and
  revised task/subscription mechanisms. The TypeScript SDK keeps 2025-era
  behavior by default and requires explicit opt-in while the revision is a
  draft.
- **Repository relevance:** The starter depends on project-scoped MCP servers
  and documents Perplexity, Firecrawl, and Playwright routing, but does not
  claim a protocol revision or provide a compatibility matrix.
- **Existing coverage:** partial
- **Scores:** relevance 4 / authority 5 / confidence 5 / impact 4 / risk 4 /
  maintenance 3 / novelty 5
- **Recommendation:** watch until the final specification is published and the
  selected MCP servers declare support. Do not update `.mcp.json`, SDKs, or
  transport assumptions from RC material.
- **Affected artifacts:** after final release,
  `docs/60-tooling/MCP_STACK.md`, `docs/60-tooling/COMPATIBILITY.md`,
  `docs/60-tooling/SOURCES.md`, and MCP doctor expectations
- **Acceptance and verification:** Re-check the final changelog on or after
  2026-07-28, record declared protocol support for each selected server, test
  version negotiation without credentials, and preserve isolated-browser and
  human-approval controls.
- **Uncertainty:** The final revision is not yet published, SDK adoption is
  asynchronous, and server behavior may remain on the 2025 protocol for an
  undetermined period.
- **Decision/PR:** Deferred until the final specification and first-party server
  compatibility statements are available. Human approval will be required for
  any dependency or transport change.
