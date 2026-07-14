---
name: security-gate
description: Perform a structured security gate before merging sensitive changes, covering threat model, auth/authz, secrets, injection, SSRF, uploads, webhooks, MCP/browser permissions, dependencies, and verification.
---

# Security gate

## 1. Classify risk

High-risk examples:
- auth/authz,
- payments,
- secrets,
- user-generated files,
- webhooks,
- admin actions,
- production data,
- arbitrary URLs,
- AI tool execution,
- browser session reuse,
- MCP write tools.

## 2. Threat model

Identify:
- assets,
- actors,
- entry points,
- trust boundaries,
- privileged operations,
- abuse cases.

## 3. Review

Check:
- authentication,
- authorization/object ownership,
- validation and encoding,
- injection,
- SSRF/open redirect,
- CSRF/CORS where relevant,
- file/path traversal,
- upload limits/type validation,
- webhook signatures/replay,
- secret leakage,
- logs/PII,
- dependency risk,
- rate limiting/abuse,
- MCP permissions,
- prompt injection.

## 4. Rank findings

- P0 critical
- P1 high
- P2 medium
- P3 low

No finding without evidence.

## 5. Verify fixes

Re-run the exploit path or failure case after remediation.

## 6. Record

Update:
- `docs/30-engineering/SECURITY_MODEL.md`
- `docs/50-evals/SECURITY_EVIDENCE.md`
- `docs/40-execution/RISKS.md` when unresolved.
