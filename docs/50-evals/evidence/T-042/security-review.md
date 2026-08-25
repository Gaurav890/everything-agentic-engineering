# T-042 runtime-baseline security review

Reviewed: 2026-08-24
Evaluator: security-reviewer
Review mode: independent, read-only review after implementation
Reviewed head: `553c747c09d93d63ac3e169f0884943c52f58942`

## Scope

Review the Claude Code 2.1.239 and Codex 0.148.0 tested-baseline change against
first-party release evidence, runtime authority boundaries, optional capability
gates, strict/advisory/JSON failure behavior, tests, and durable guidance. The
review did not edit files, push, comment, approve, finalize, or merge.

## Findings and corrections

No blocking security defect or accidental authority expansion was found.

The review required three workflow corrections before finalization:

1. Record the independent review in the task evidence bundle.
2. Replace the stale handoff instruction that still said to open the existing
   draft pull request.
3. Use the normal task finish and bounded finalization commands instead of
   manually editing the task ledger.

## Verified boundaries

- Runtime floors and source URLs match the reviewed official releases.
- Hardening behaviors are separate from repository authorization.
- Claude marketplace/MCP `headersHelper` remains disabled and human-gated.
- Codex asynchronous or MCP-invoking hooks remain disabled and human-gated.
- No runtime, hook, MCP, plugin, credential, network, sandbox, provider, model,
  data, deployment, production, approval, or merge configuration changed.
- Compatibility guidance retains uncertainty because upstream release notes do
  not publish CVEs, complete affected-version ranges, or exploit prerequisites.

## Evidence

- Eight focused runtime compatibility tests pass.
- Strict simulation rejects Claude Code 2.1.238 and Codex 0.147.0.
- Strict simulation accepts Claude Code 2.1.239 and Codex 0.148.0.
- Optional capability output says `human approval required; not enabled`.
- Manifest JSON, all 41 task records, and `git diff --check` validate.
- GitHub `verify` and `policy` checks passed on the reviewed head.
- Full repository verification passed all ten stages before review.

## Residual uncertainty

The first-party release notes support conservative tested floors, not a claim
that every earlier installation is exploitable. Optional helpers and hooks
still need separate threat models before any project enables them.

## Verdict

**PASS.** No blocking or material non-blocking security finding remains. Human
task finalization and squash merge remain separate decisions.
