# Handoff

Last updated: 2026-08-24

## Current goal

Finish verification and human/security review of the tested runtime-security
baseline update.

## Completed

- Raised the machine-readable Claude Code tested floor from 2.1.233 to 2.1.239.
- Raised the machine-readable Codex tested floor from 0.147.0 to 0.148.0.
- Recorded the cumulative permission, filesystem, credential, marketplace,
  MCP trust, organization-policy, resumed-state, and instruction-state fixes
  from official release notes.
- Kept Claude marketplace/MCP `headersHelper` commands and Codex asynchronous or
  MCP-invoking hooks disabled and explicitly human-gated.
- Updated strict/advisory/JSON regression coverage and compatibility guidance.

## Blockers

- No known implementation blocker.
- Independent security review and full repository verification are required
  before direct human task approval.

## Unresolved decisions

- Whether any project should later enable a marketplace/MCP helper or an
  asynchronous/MCP-invoking hook. Each requires a separate threat model,
  authority decision, rollback plan, and review; compatibility alone is not
  authorization.

## Verification status

- Eight focused runtime-policy tests pass.
- Strict simulation rejects Claude Code 2.1.238 and Codex 0.147.0, and accepts
  Claude Code 2.1.239 and Codex 0.148.0.
- JSON output validates with `mutation_performed: false`.
- Full repository verification passes all ten stages.
- The installed Codex runtime reports `0.148.0-alpha.21`, so the advisory doctor
  correctly warns that it is below the stable 0.148.0 floor; no upgrade occurs.
- No runtime was installed, upgraded, or configured by this task.
- No optional capability was enabled.

## Exact next action

Open a draft pull request for issue #62 and obtain independent security review.
Do not finalize the task or mark the pull request ready from CI evidence alone.

## Relevant files

- `.agentic/runtime-baselines.json`
- `tests/test_runtime_compatibility.py`
- `docs/60-tooling/COMPATIBILITY.md`
- `docs/60-tooling/CODEX.md`
- `docs/60-tooling/INSTALLATION.md`
- `docs/30-engineering/SECURITY_MODEL.md`
- `docs/60-tooling/LEARNING_LEDGER.md`

Keep this concise enough to read in under two minutes.
