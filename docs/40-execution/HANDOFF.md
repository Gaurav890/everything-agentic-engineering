# Handoff

Last updated: 2026-08-13

## Current goal

Adopt the Agent Plugins 1.0 portable package contract without breaking the
existing Codex-native adapter or widening plugin/MCP authority.

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

## Blockers

- None.

## Unresolved decisions

- Portable MCP packaging requires a separate compatibility matrix for the
  selected servers, transports, protocol revisions, credentials, and clients.
- Native compatibility files may be removed only after every supported client
  passes installation and discovery tests.
- Publishing or installation remains a human-owned release decision.

## Verification status

- Portable manifest, skill containment, native-manifest drift, project-MCP
  separation, command discovery, and negative-fixture tests pass locally.
- Full repository verification passes all ten stages across profiles, tokens,
  security hooks, runtime/Codex policy, local links, and Showcase checks.

## Exact next action

Run `./agentic doctor plugin` whenever portable package metadata or shared
skills change. Treat any portable MCP proposal as a separate compatibility
decision rather than copying `.mcp.json` into root `mcp.json`.

## Relevant files

- `plugin.json`
- `.codex-plugin/plugin.json`
- `skills/`
- `docs/60-tooling/AGENT_PLUGINS.md`
- `scripts/validate_agent_plugin.py`
- `tests/test_agent_plugin.py`

Keep this concise enough to read in under two minutes.
