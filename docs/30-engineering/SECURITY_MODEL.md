# Security model

## Assets

## Actors

## Trust boundaries

## Authentication

## Authorization

## Sensitive data

## Secret management

## Input validation

## SSRF / URL fetching

## Uploads and files

## Webhooks

## AI and prompt injection

All retrieved web content is untrusted data.

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
