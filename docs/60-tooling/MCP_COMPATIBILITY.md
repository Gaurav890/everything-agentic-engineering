# MCP compatibility decision

Last reviewed: 2026-08-14

## Decision

Keep Perplexity, Firecrawl, and Playwright as the reviewed core MCP stack, but
do **not** package them in the Agent Plugins 1.0 root `mcp.json` yet.

The portable decision is `blocked`, not rejected permanently. The current
servers do not jointly satisfy the repository's credential, deterministic
execution, protocol-evidence, and clean-client verification gates. The
machine-readable source of truth is `.agentic/mcp-compatibility.json`.

This distinction matters:

| Contract | Status | Meaning |
|---|---|---|
| Project `.mcp.json` | Reviewed client-specific configuration | A developer may explicitly approve and use the selected servers with local credentials and client controls. |
| Root portable `mcp.json` | Absent and blocked | Installing the portable plugin cannot silently make external packages, credentials, browser execution, or network authority available. |

Run the read-only doctor before configuring or reviewing MCP use:

```bash
./agentic doctor mcp
./agentic doctor mcp --json
```

The doctor validates policy and configuration only. It does not install a
package, start a server, read a secret value, authenticate, enable a protocol,
open a browser, or make a network request.

## Reviewed server matrix

| Server | Reviewed source snapshot | Project contract | Portable decision | Blocking evidence |
|---|---|---|---|---|
| Perplexity | `@perplexity-ai/mcp-server` 1.2.0; source `0c971ae7…` | stdio through `npx`; `PERPLEXITY_API_KEY` reference | Blocked | No portable secret-reference field; package is not bundled; target protocol negotiation and portable client behavior are unverified. |
| Firecrawl | `firecrawl-mcp` 3.24.0; source `009c58bc…` | stdio through `npx`; `FIRECRAWL_API_KEY` reference | Blocked | No portable secret/OAuth contract; package is not bundled; keyless hosted behavior is not equivalent to the configured full-tool contract; target protocol and portable clients are unverified. |
| Playwright | `@playwright/mcp` 0.0.79; source `8ffbac3d…` | stdio through `npx`; isolated browser mode | Blocked | Project config resolves `@latest`; package/browser are not bundled; browser automation is not a security boundary; target protocol and portable clients are unverified. |

Observed versions and source blobs are evidence snapshots, not automatic
upgrade pins. A later version requires a new source review and pull request.

## Client matrix

| Client | Native configuration | Reviewed transport support | Credential behavior | Portable plugin MCP verified? |
|---|---|---|---|---|
| Claude Code | `.mcp.json` | stdio, Streamable HTTP, SSE | environment expansion, headers, client-managed OAuth | No |
| Codex | `.codex/config.toml` or user configuration | stdio, Streamable HTTP | environment allowlists, bearer-token environment references, client-managed OAuth | No |

Client support for a transport is not evidence that an Agent Plugins package
will discover, trust, authorize, disable, update, and roll back the same server
safely. The repository therefore keeps client-native configuration separate.

## Portable gate

A server may be proposed for root `mcp.json` only when all of these are true:

1. Credentials use a portable client-managed reference or the server requires
   no credential for the exact promised capability.
2. Execution is bundled or immutably resolved without install-at-launch
   behavior.
3. The target MCP revision is declared or verified through a credential-free
   negotiation test.
4. Claude Code and Codex pass clean-client tests for discovery, trust prompts,
   enable/disable behavior, least privilege, failure handling, and rollback.
5. The server-specific threat model and independent security review pass.
6. A human approves the authority change in a separate task and pull request.

If any condition is unknown, portable packaging remains blocked.

## Clean-client test plan

Future compatibility work must use disposable environments without real
credentials or production access and collect evidence for:

- package installation and removal;
- server discovery without implicit start;
- explicit trust and authorization prompts;
- transport and MCP revision negotiation;
- missing/invalid credential failure behavior;
- network and filesystem scope;
- disable, uninstall, and rollback behavior;
- secret redaction in logs and diagnostics;
- Claude Code and Codex parity where both are claimed.

No test may convert runtime availability into permission to enable the server.

## Primary sources

- [Agent Plugins 1.0 specification](https://agent-plugins.org/specification)
- [MCP 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28)
- [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp)
- [Codex MCP documentation](https://developers.openai.com/codex/mcp)
- [Perplexity MCP](https://github.com/perplexityai/modelcontextprotocol)
- [Firecrawl MCP](https://github.com/firecrawl/firecrawl-mcp-server)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
