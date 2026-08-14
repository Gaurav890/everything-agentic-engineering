# T-035 MCP compatibility security review

Reviewed: 2026-08-14
Required specialist contract: Identity & Access Engineer
Review mode: independent evidence pass after implementation

## Scope

Review the proposed portable MCP compatibility policy and doctor. No server was
installed, started, authenticated, or contacted during this task.

## Identities and trust boundaries

| Identity / boundary | Authority | Required control |
|---|---|---|
| Plugin installer | Places package content on disk | Must not silently grant MCP execution or network access. |
| MCP client | Discovers, trusts, starts, and authorizes servers | Client-specific approval and managed policy remain authoritative. |
| Local MCP process | Executes with the invoking user's permissions | Use reviewed package resolution, least privilege, and explicit start. |
| Remote MCP service | Receives queries and may return untrusted data | Scope credentials and treat every response as untrusted. |
| Perplexity / Firecrawl API credential | Grants paid external-service access | Keep only in environment or secure client storage; never package or print values. |
| Playwright browser session | Can reach sites and hold cookies/storage | Default to isolated sessions; treat state as secret; browser automation is not a sandbox. |

## Findings

1. **Portable credential ambiguity — blocking.** Agent Plugins 1.0 does not
   provide a portable secret-reference or OAuth configuration field. Packaging
   credential-bearing project configuration would either expose data or create
   client-dependent behavior.
2. **Install-at-launch execution — blocking.** All three project entries use
   external `npx` packages. Playwright additionally resolves `@latest`. A
   portable declaration would therefore imply unreviewed package acquisition
   or mutable execution unless separately pinned and bundled.
3. **Client trust parity — blocking.** Claude Code and Codex have native MCP
   configuration and credential controls, but portable plugin discovery,
   prompts, disable behavior, and rollback have not passed clean-client tests.
4. **Protocol claim — blocking.** MCP 2026-07-28 is the target revision, but the
   three servers have not supplied or passed sufficient negotiation evidence
   for this portable contract.
5. **Browser authority — blocking.** Playwright MCP can operate a browser with
   the user's reach and is explicitly not a security boundary. `--isolated`
   reduces persistent-state risk but does not authorize arbitrary navigation.

## Controls verified

- Root `mcp.json` is absent while portable packaging is blocked.
- The plugin validator rejects even an empty root `mcp.json` under the blocked
  policy, preventing misleading partial packaging.
- Project `.mcp.json` retains only the three reviewed servers, environment
  references instead of literal credentials, and Playwright isolated mode.
- Human and JSON doctor output reveal credential names only, never values.
- The doctor is offline and declares both server execution and mutation false.
- Negative tests reject literal secrets, unknown servers, premature client
  verification, and blocked portable manifests.

## Decision

**PASS for the blocked-by-default compatibility policy and read-only doctor.**

**FAIL for portable MCP packaging at this time.** A new human-approved task is
required after every gate in `docs/60-tooling/MCP_COMPATIBILITY.md` has evidence.
