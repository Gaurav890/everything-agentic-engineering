# Handoff

Last updated: 2026-08-16

## Current goal

Review the evidence-backed Claude Code 2.1.233 advisory baseline and its
documented exceptions before human finalization.

## Completed

- The machine-readable recommended minimum is 2.1.233 and points to the exact
  first-party release.
- The policy records Windows NT device-prefix validation, literal skill-argument
  substitution, and MCP v2 subscription reliability as versioned behavior.
- The 2.1.232 Cygwin-symlink and Bash input-redirection permission changes are
  explicitly recorded as reverted and excluded from the 2.1.233 guarantee.
- Apps-gateway user-identity forwarding is disabled and human-gated pending a
  separate privacy and proxy-trust review.
- Installation, runtime configuration, credentials, network/sandbox changes,
  external integration enablement, deployment, production, approval, and merge
  remain outside the task.

## Blockers

- None.

## Unresolved decisions

- The release note does not publish a CVE, complete affected-version range, or
  exploit prerequisites for the NTLM issue.
- The MCP statement proves a client reliability fix, not universal server
  compatibility or authorization to connect one.

## Verification status

- Eight targeted runtime compatibility tests pass.
- Strict simulation rejects 2.1.232 and accepts 2.1.233.
- JSON reporting declares `mutation_performed: false`.
- The independent security review passes after correcting the reverted
  permission and identity-forwarding boundaries.
- Full repository verification passes all ten stages.

## Exact next action

For work that reaches human review, use the bounded finalization contract in
`docs/70-collaboration/GITHUB_WORKFLOW.md`. Human approval authorizes only the
linked task-ledger transition; squash merge remains a separate human action.

## Relevant files

- `.agentic/runtime-baselines.json`
- `tests/test_runtime_compatibility.py`
- `docs/60-tooling/COMPATIBILITY.md`
- `docs/60-tooling/LEARNING_LEDGER.md`
- `docs/30-engineering/SECURITY_MODEL.md`
- `docs/50-evals/evidence/T-038/security-review.md`

Keep this concise enough to read in under two minutes.
