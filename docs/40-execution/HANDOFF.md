# Handoff

Last updated: 2026-08-14

## Current goal

Review and merge the evidence-backed portable MCP compatibility decision
without enabling or packaging any server.

## Completed

- T-031 added the read-only capability decision engine.
- T-032 added the disabled, plan-only Prime Agent adapter.
- T-033 added the project-local, plan-only selective Agency Agents installer.
- Root `plugin.json` now carries only Agent Plugins 1.0 portable metadata.
- Root `skills/` remains the contained fixed discovery path for the canonical
  project-local skill catalog.
- `.codex-plugin/plugin.json` remains a separate Codex-native compatibility
  surface, and `.mcp.json` remains project-local.
- `./agentic doctor plugin` validates the portable contract offline.
- T-035 records the Perplexity, Firecrawl, Playwright, Claude Code, and Codex
  compatibility matrix in `.agentic/mcp-compatibility.json`.
- `./agentic doctor mcp` validates the decision and project configuration
  without reading secret values, starting servers, or making network requests.
- Root `mcp.json` is absent and rejected while portable packaging is blocked.

## Blockers

- None.

## Unresolved decisions

- Portable MCP packaging may be reconsidered only after every gate in
  `MCP_COMPATIBILITY.md` passes clean-client and security review.
- Native compatibility files may be removed only after every supported client
  passes installation and discovery tests.
- Publishing or installation remains a human-owned release decision.

## Verification status

- Compatibility and portable-plugin unit tests pass, including negative
  fixtures for literal credentials, unknown servers, premature client claims,
  and blocked root manifests.
- Full repository verification passes all ten stages; T-035 is in `review`.

## Exact next action

Keep portable MCP packaging blocked until every documented gate has evidence.
Any future proposal must be a new human-approved task; never copy `.mcp.json`
into root `mcp.json`.

## Relevant files

- `plugin.json`
- `.codex-plugin/plugin.json`
- `skills/`
- `docs/60-tooling/AGENT_PLUGINS.md`
- `.agentic/mcp-compatibility.json`
- `docs/60-tooling/MCP_COMPATIBILITY.md`
- `docs/50-evals/evidence/T-035/security-review.md`
- `scripts/mcp_compatibility.py`
- `scripts/validate_agent_plugin.py`
- `tests/test_agent_plugin.py`

Keep this concise enough to read in under two minutes.
