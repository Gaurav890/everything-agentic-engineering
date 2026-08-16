# T-036 runtime-baseline security review

Reviewed: 2026-08-14
Evaluator: security-reviewer
Review mode: independent, read-only review after implementation

## Scope

Review the Claude Code 2.1.232 compatibility-floor change against identity,
authorization, multi-agent, context, failure, test, and mutation boundaries.
The review did not install, upgrade, configure, authenticate, or enable a
runtime or external capability.

## Required specialist coverage

| Contract | Evidence | Result |
|---|---|---|
| Identity & Access Engineer | Cross-session names are rejected as identity proofs; optional cross-session, self-hosted, MCP, marketplace, Remote Control, and sandbox authority stays human-gated. | PASS |
| Multi-Agent Systems Architect | Fork context, read-only roles, isolated writers, bounded timeout/retry, terminal states, fail-closed interruption, and evaluator handoff are explicit. | PASS |
| Accessibility Auditor | No UI, interaction, rendered surface, or frontend behavior changed. | NOT APPLICABLE |

## Findings

No blocking findings.

The evaluator requested four non-blocking corrections, all applied before final
verification:

1. Background work now requires a bounded timeout/retry budget and explicit
   terminal state; missing or interrupted results fail closed.
2. Compatibility guidance now states that `default_enabled: true` records
   tested upstream hardening/runtime behavior and is not repository action
   authorization.
3. Tests now assert every human-gated Claude capability is disabled by default.
4. Tests now assert the minimum versions for both newly recorded hardening
   capabilities.

## Trust and authority decision

- Bare cross-session names are convenience identifiers, not authentication or
  authorization.
- A full-context fork receives only the context needed for a bounded task;
  unrelated secrets are not intentionally delegated.
- In-session specialists remain read-only. Write-capable workers still require
  isolated branches/worktrees and one accountable owner.
- Background execution does not prove completion and grants no approval,
  deployment, production, or merge authority.
- Optional authority-expanding capabilities remain `default_enabled: false`
  and `human_approval_required: true`.
- The doctor remains advisory/read-only and declares
  `mutation_performed: false`.

## Verification verdict

**PASS.** The tested baseline may move to 2.1.232 with the documented project
contract. Runtime installation/upgrades, new settings, optional capability
activation, approval, and merge remain separate human decisions.
